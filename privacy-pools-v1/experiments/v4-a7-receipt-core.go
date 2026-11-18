package main

import (
	"bufio"
	"crypto/hmac"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/hex"
	"errors"
	"fmt"
	"strings"
)

const (
	credentialDomain = "kohaku-key/v3-r3/privacy-pools-v1/deriveAt"
	credentialPath   = "m/28784'/1'/0'"
	receiptDomain    = "kohaku-key/v4-a7/privacy-pools-v1/receipt"
)

func receiptTag(root *[32]byte, challenge []byte) []byte {
	first := hmac.New(sha256.New, root[:])
	first.Write([]byte(credentialDomain))
	first.Write([]byte{0})
	first.Write([]byte(credentialPath))
	credential := first.Sum(nil)
	defer clear(credential)

	second := hmac.New(sha256.New, credential)
	second.Write([]byte(receiptDomain))
	second.Write([]byte{0})
	second.Write(challenge)
	return second.Sum(nil)
}

func verify(root *[32]byte, challenge, tag []byte) bool {
	if len(challenge) != 16 || len(tag) != 32 {
		return false
	}
	expected := receiptTag(root, challenge)
	defer clear(expected)
	return subtle.ConstantTimeCompare(expected, tag) == 1
}

func selfTest() error {
	var root [32]byte
	var challenge [16]byte
	for i := range root {
		root[i] = byte(i)
	}
	for i := range challenge {
		challenge[i] = byte(i)
	}
	defer clear(root[:])

	expected, err := hex.DecodeString(
		"e471d50c0e8b5e6b5784d3a9ee094bb48aebb1008dd48d040066ed9cfc6d7e41",
	)
	if err != nil || !verify(&root, challenge[:], expected) {
		return errors.New("synthetic receipt mismatch")
	}

	expected[0] ^= 1
	if verify(&root, challenge[:], expected) {
		return errors.New("tampered receipt accepted")
	}

	fmt.Println("PASS: Synthetic V3-to-V4 receipt compatibility")
	fmt.Println("PASS: Tampered receipt rejected")
	return nil
}

func readHex(reader *bufio.Reader, prompt string, size int) ([]byte, error) {
	fmt.Print(prompt)
	line, err := reader.ReadString('\n')
	if err != nil {
		return nil, errors.New("receipt input failed")
	}
	value, err := hex.DecodeString(strings.TrimSpace(line))
	if err != nil || len(value) != size {
		return nil, errors.New("invalid receipt field length or encoding")
	}
	return value, nil
}
