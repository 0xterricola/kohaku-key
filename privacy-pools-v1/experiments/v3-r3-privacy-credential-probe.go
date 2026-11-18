package main

import (
	"bytes"
	"encoding/hex"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"

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

// Node receives two 32-byte roots on anonymous descriptor 3.
// Its source contains no secret values.
const nodeProbe = `
import { readSync } from "node:fs";
import { createHmac } from "node:crypto";
import { isDeepStrictEqual } from "node:util";
import { SecretManager } from "@kohaku-eth/privacy-pools";

const input = Buffer.alloc(64);
const rootA = Buffer.alloc(32);
const rootB = Buffer.alloc(32);

function check(condition, message) {
  if (!condition) throw new Error(message);
}

function manager(root) {
  return SecretManager({
    accountIndex: 0,
    host: {
      keystore: {
        async deriveAt(keyPath) {
          check(
            /^m\/28784'\/1'(?:\/(?:0|[1-9][0-9]*)')+$/.test(keyPath),
            "Unexpected SDK derivation path"
          );

          const derived = createHmac("sha256", root)
            .update("kohaku-key/v3-r3/privacy-pools-v1/deriveAt")
            .update("\0")
            .update(keyPath)
            .digest();

          const result = "0x" + derived.toString("hex");
          derived.fill(0);
          return result;
        },
      },
    },
  });
}

try {
  let offset = 0;
  while (offset < input.length) {
    const count = readSync(3, input, offset, input.length - offset, null);
    check(count > 0, "Incomplete private IPC transfer");
    offset += count;
  }

  input.copy(rootA, 0, 0, 32);
  input.copy(rootB, 0, 32, 64);
  input.fill(0);

  const first = manager(rootA);
  const recovered = manager(rootB);

  const context = {
    chainId: 11155111n,
    entrypointAddress:
      0x34A2068192b1297f2a7f85D7D8CdE66F8F0921cBn,
    depositIndex: 0,
  };

  const a = await first.getDepositSecrets(context);
  const b = await recovered.getDepositSecrets(context);

  check(isDeepStrictEqual(a, b), "Deposit recovery mismatch");
  console.log("PASS: Hardware-derived deposit reconstruction");

  const withdrawal = { ...context, withdrawIndex: 1 };

  const wa = await first.getSecrets(withdrawal);
  const wb = await recovered.getSecrets(withdrawal);

  check(isDeepStrictEqual(wa, wb), "Withdrawal recovery mismatch");
  console.log("PASS: Hardware-derived withdrawal reconstruction");

  const signerA = await first.deriveEphemeralSigner(withdrawal);
  const signerB = await recovered.deriveEphemeralSigner(withdrawal);

  check(signerA === signerB, "Ephemeral signer mismatch");
  console.log("PASS: Hardware-derived ephemeral signer reproduction");

  const next = await first.getDepositSecrets({
    ...context,
    depositIndex: 1,
  });

  check(
    a.precommitment !== next.precommitment,
    "Deposit index collision"
  );
  console.log("PASS: Deposit index separation");

  const otherChain = await first.getDepositSecrets({
    ...context,
    chainId: 1n,
  });

  check(
    a.precommitment !== otherChain.precommitment,
    "Chain separation failed"
  );
  console.log("PASS: Chain separation");

  console.log("PASS: V3-R3 offline credential reconstruction");
} catch {
  console.error("FAIL: R3 credential reconstruction");
  process.exitCode = 1;
} finally {
  input.fill(0);
  rootA.fill(0);
  rootB.fill(0);
}
`

func runNode(first, second *[32]byte) error {
	readEnd, writeEnd, err := os.Pipe()
	if err != nil {
		return errors.New("anonymous pipe creation failed")
	}
	defer readEnd.Close()
	defer writeEnd.Close()

	home, err := os.UserHomeDir()
	if err != nil {
		return errors.New("home directory unavailable")
	}

	cmd := exec.Command(
		"node",
		"--import", "tsx",
		"--input-type=module",
		"--eval", nodeProbe,
	)
	cmd.Dir = filepath.Join(home, "Developer/kohaku-cli")
	cmd.ExtraFiles = []*os.File{readEnd}
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	// Prevent inherited Node debugging flags.
	cmd.Env = append(os.Environ(), "NODE_OPTIONS=")

	if err := cmd.Start(); err != nil {
		return errors.New("Node adapter startup failed")
	}

	readEnd.Close()

	payload := make([]byte, 64)
	copy(payload[:32], first[:])
	copy(payload[32:], second[:])

	_, writeErr := writeEnd.Write(payload)
	clear(payload)
	writeEnd.Close()

	waitErr := cmd.Wait()
	if writeErr != nil || waitErr != nil {
		return errors.New("Node credential adapter failed")
	}
	return nil
}

func run() error {
	for _, name := range []string{
		"KEYCARD_PIN", "KEYCARD_PUK", "KEYCARD_PAIRING_PASSWORD",
	} {
		if _, exists := os.LookupEnv(name); exists {
			return errors.New("legacy secret environment variable must be unset")
		}
	}

	fmt.Println("=== Authenticated hardware session 1 ===")
	first, err := acquire()
	if err != nil {
		return err
	}
	defer clear(first[:])
	fmt.Println("PASS: BIP-85 root acquired in memory")

	fmt.Println("=== Authenticated hardware session 2 ===")
	second, err := acquire()
	if err != nil {
		return err
	}
	defer clear(second[:])

	if !bytes.Equal(first[:], second[:]) {
		return errors.New("hardware root mismatch")
	}
	fmt.Println("PASS: Hardware root reconstructed across sessions")

	fmt.Println("=== Privacy Pools SDK reconstruction ===")
	return runNode(&first, &second)
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "FAIL:", err)
		os.Exit(1)
	}
}
