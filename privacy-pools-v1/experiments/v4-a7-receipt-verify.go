package main

import (
	"bufio"
	"bytes"
	"encoding/hex"
	"errors"
	"fmt"
	"os"

	"github.com/ebfe/scard"
	keycard "github.com/keycard-tech/keycard-go/v4"
	keycardio "github.com/keycard-tech/keycard-go/v4/io"
	"golang.org/x/term"
)

const (
	reader       = "HID Global OMNIKEY 3x21 Smart Card Reader"
	testCA       = "025877220AAAE6E54A6F974602D5995C0FE24A3EA7DDABD8644BEC795B9DA00743"
	cardIdentity = "03475c427cea8ec434adc771c3424a3d31f49c2b89f98db530e845461c285ebf09"
	bip85Path    = "m/83696968'/128169'/32'/0'"
)

func acquire() (root [32]byte, err error) {
	ctx, err := scard.EstablishContext()
	if err != nil {
		return root, errors.New("PC/SC unavailable")
	}
	defer ctx.Release()

	card, err := ctx.Connect(reader, scard.ShareShared, scard.ProtocolAny)
	if err != nil {
		return root, errors.New("card connection failed")
	}
	defer card.Disconnect(scard.ResetCard)

	rawCA, err := hex.DecodeString(testCA)
	if err != nil || len(rawCA) != 33 {
		return root, errors.New("invalid test CA")
	}

	var ca [33]byte
	copy(ca[:], rawCA)

	kc := keycard.NewCommandSetWithCA(
		keycardio.NewNormalChannel(card), ca,
	)

	if err := kc.Select(); err != nil {
		return root, errors.New("certificate authentication failed")
	}

	info := kc.ApplicationInfo
	identity, err := hex.DecodeString(cardIdentity)
	if err != nil {
		return root, errors.New("invalid identity configuration")
	}

	if info == nil || info.AppVersion() != 0x0400 ||
		len(info.CertData) < 33 ||
		!bytes.Equal(info.CertData[:33], identity) {
		return root, errors.New("unexpected card identity or version")
	}

	if err := kc.AutoOpenSecureChannel(); err != nil {
		return root, errors.New("secure channel failed")
	}

	tty, err := os.OpenFile("/dev/tty", os.O_RDWR, 0)
	if err != nil {
		return root, errors.New("interactive terminal required")
	}
	defer tty.Close()

	fmt.Fprint(tty, "Keycard 4.0 PIN: ")
	pin, err := term.ReadPassword(int(tty.Fd()))
	fmt.Fprintln(tty)

	if err != nil || len(pin) == 0 || len(pin) > 64 {
		clear(pin)
		return root, errors.New("PIN entry cancelled or invalid")
	}

	// PIN is never supplied via argv, env, or files.
	err = kc.VerifyPIN(string(pin))
	clear(pin)
	if err != nil {
		return root, errors.New("PIN verification failed; no retry attempted")
	}

	material, err := kc.ExportBIP85(bip85Path, 32)
	if err != nil || len(material) != 32 {
		clear(material)
		return root, errors.New("BIP-85 derivation failed")
	}

	copy(root[:], material)
	clear(material)
	return root, nil
}

func hardwareVerify() error {
	for _, name := range []string{
		"KEYCARD_PIN", "KEYCARD_PUK", "KEYCARD_PAIRING_PASSWORD",
	} {
		if _, exists := os.LookupEnv(name); exists {
			return errors.New("legacy secret environment variable must be unset")
		}
	}

	reader := bufio.NewReader(os.Stdin)
	challenge, err := readHex(reader, "Shell challenge (32 hex): ", 16)
	if err != nil {
		return err
	}
	tag, err := readHex(reader, "Shell tag (64 hex): ", 32)
	if err != nil {
		return err
	}

	root, err := acquire()
	if err != nil {
		return err
	}
	defer clear(root[:])

	if !verify(&root, challenge, tag) {
		return errors.New("Shell receipt does not match V3 reference")
	}

	fmt.Println("PASS: Shell receipt matches V3 hardware derivation")
	return nil
}

func main() {
	var err error
	switch {
	case len(os.Args) == 2 && os.Args[1] == "--hardware":
		err = hardwareVerify()
	default:
		err = errors.New("usage: verifier --hardware")
	}

	if err != nil {
		fmt.Fprintln(os.Stderr, "FAIL:", err)
		os.Exit(1)
	}
}
