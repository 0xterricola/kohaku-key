package main

import (
	"bytes"
	"crypto/elliptic"
	"encoding/hex"
	"errors"
	"fmt"
	"os"

	"github.com/ebfe/scard"
	"github.com/ethereum/go-ethereum/crypto"
	keycard "github.com/keycard-tech/keycard-go/v4"
	keycardio "github.com/keycard-tech/keycard-go/v4/io"
	"golang.org/x/term"
)

const (
	reader = "HID Global OMNIKEY 3x21 Smart Card Reader"
	testCA = "025877220AAAE6E54A6F974602D5995C0FE24A3EA7DDABD8644BEC795B9DA00743"

	bip0     = "m/83696968'/128169'/32'/0'"
	bip1     = "m/83696968'/128169'/32'/1'"
	ecdhPath = "m/43'/60'/1581'/0'/0"
)

type sample struct {
	cert []byte
	b0   []byte
	b1   []byte
	e0   []byte
	e1   []byte
}

func (s *sample) wipe() {
	clear(s.cert)
	clear(s.b0)
	clear(s.b1)
	clear(s.e0)
	clear(s.e1)
}

func verifyPIN(kc *keycard.CommandSet) error {
	tty, err := os.OpenFile("/dev/tty", os.O_RDWR, 0)
	if err != nil {
		return errors.New("interactive terminal required")
	}
	defer tty.Close()

	fmt.Fprint(tty, "Keycard 4.0 PIN: ")
	pinBytes, err := term.ReadPassword(int(tty.Fd()))
	fmt.Fprintln(tty)

	if err != nil {
		clear(pinBytes)
		return errors.New("PIN entry cancelled")
	}

	if len(pinBytes) == 0 || len(pinBytes) > 64 {
		clear(pinBytes)
		return errors.New("invalid PIN length")
	}

	pin := string(pinBytes)
	clear(pinBytes)

	err = kc.VerifyPIN(pin)
	pin = ""

	if err != nil {
		return errors.New("PIN verification failed")
	}
	return nil
}

func acquire(peerA, peerB []byte) (out sample, err error) {
	defer func() {
		if err != nil {
			out.wipe()
		}
	}()

	ctx, err := scard.EstablishContext()
	if err != nil {
		return out, errors.New("PC/SC context failed")
	}
	defer ctx.Release()

	card, err := ctx.Connect(
		reader,
		scard.ShareShared,
		scard.ProtocolAny,
	)
	if err != nil {
		return out, errors.New("card connection failed")
	}
	defer card.Disconnect(scard.ResetCard)

	rawCA, err := hex.DecodeString(testCA)
	if err != nil || len(rawCA) != 33 {
		return out, errors.New("invalid test CA configuration")
	}

	var ca [33]byte
	copy(ca[:], rawCA)

	kc := keycard.NewCommandSetWithCA(
		keycardio.NewNormalChannel(card),
		ca,
	)

	// SELECT validates the card certificate against our test CA.
	if err := kc.Select(); err != nil {
		return out, errors.New("card selection or certificate verification failed")
	}

	if kc.ApplicationInfo == nil ||
		kc.ApplicationInfo.AppVersion() != 0x0400 {
		return out, errors.New("expected Keycard applet 4.0")
	}

	out.cert = bytes.Clone(kc.ApplicationInfo.CertData)
	if len(out.cert) == 0 {
		return out, errors.New("missing authenticated card certificate")
	}

	if err := kc.AutoOpenSecureChannel(); err != nil {
		return out, errors.New("authenticated secure channel failed")
	}

	if err := verifyPIN(kc); err != nil {
		return out, err
	}

	out.b0, err = kc.ExportBIP85(bip0, 32)
	if err != nil || len(out.b0) != 32 {
		return out, errors.New("BIP-85 index 0 failed")
	}

	repeated, opErr := kc.ExportBIP85(bip0, 32)
	if opErr != nil {
		return out, errors.New("BIP-85 repetition failed")
	}
	equal := bytes.Equal(out.b0, repeated)
	clear(repeated)
	if !equal {
		return out, errors.New("BIP-85 nondeterministic within session")
	}

	out.b1, err = kc.ExportBIP85(bip1, 32)
	if err != nil || len(out.b1) != 32 {
		return out, errors.New("BIP-85 index 1 failed")
	}

	out.e0, err = kc.ECDH(peerA, ecdhPath)
	if err != nil || len(out.e0) != 32 {
		return out, errors.New("ECDH peer A failed")
	}

	out.e1, err = kc.ECDH(peerB, ecdhPath)
	if err != nil || len(out.e1) != 32 {
		return out, errors.New("ECDH peer B failed")
	}

	return out, nil
}

func run() error {
	// G and 2G are public secp256k1 points.
	// No peer private keys are generated or stored.
	curve := crypto.S256()
	gx, gy := curve.Params().Gx, curve.Params().Gy
	x2, y2 := curve.Double(gx, gy)

	peerA := elliptic.Marshal(curve, gx, gy)
	peerB := elliptic.Marshal(curve, x2, y2)

	fmt.Println("=== Session 1 ===")
	first, err := acquire(peerA, peerB)
	if err != nil {
		return err
	}
	defer first.wipe()

	fmt.Println("PASS: First authenticated hardware session")

	fmt.Println("=== Session 2 ===")
	second, err := acquire(peerA, peerB)
	if err != nil {
		return err
	}
	defer second.wipe()

	if !bytes.Equal(first.cert, second.cert) {
		return errors.New("card identity changed between sessions")
	}
	fmt.Println("PASS: Same authenticated card across sessions")

	if !bytes.Equal(first.b0, second.b0) ||
		!bytes.Equal(first.b1, second.b1) {
		return errors.New("BIP-85 cross-session mismatch")
	}
	fmt.Println("PASS: BIP-85 reproducibility across sessions")

	if bytes.Equal(first.b0, first.b1) {
		return errors.New("BIP-85 index separation failed")
	}
	fmt.Println("PASS: BIP-85 index separation")

	if !bytes.Equal(first.e0, second.e0) ||
		!bytes.Equal(first.e1, second.e1) {
		return errors.New("ECDH cross-session mismatch")
	}
	fmt.Println("PASS: ECDH reproducibility across sessions")

	if bytes.Equal(first.e0, first.e1) {
		return errors.New("ECDH peer separation failed")
	}
	fmt.Println("PASS: ECDH peer separation")

	fmt.Println("PASS: V3-R2 physical hardware checkpoint")
	return nil
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "FAIL:", err)
		os.Exit(1)
	}
}
