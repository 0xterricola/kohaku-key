package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

type r4PublicResult struct {
	Deposit    string `json:"deposit"`
	Withdrawal string `json:"withdrawal"`
}

// Reuse the frozen R3 SDK derivation contract.
// Only add an IPC return of public note precommitments.
func r4Script() (string, error) {
	source := nodeProbe

	oldImport := `import { readSync } from "node:fs";`
	newImport := `import { readSync, writeSync } from "node:fs";`

	if strings.Count(source, oldImport) != 1 {
		return "", errors.New("R3 import contract changed")
	}

	source = strings.Replace(source, oldImport, newImport, 1)

	anchor := `console.log("PASS: V3-R3 offline credential reconstruction");`

	if strings.Count(source, anchor) != 1 {
		return "", errors.New("R3 completion contract changed")
	}

	injected := anchor + `
  writeSync(4, Buffer.from(JSON.stringify({
    deposit: String(a.precommitment),
    withdrawal: String(wa.precommitment)
  })));`

	return strings.Replace(source, anchor, injected, 1), nil
}

func r4Compute(root *[32]byte) (r4PublicResult, error) {
	var result r4PublicResult

	source, err := r4Script()
	if err != nil {
		return result, err
	}

	secretRead, secretWrite, err := os.Pipe()
	if err != nil {
		return result, errors.New("secret IPC setup failed")
	}
	defer secretRead.Close()
	defer secretWrite.Close()

	publicRead, publicWrite, err := os.Pipe()
	if err != nil {
		return result, errors.New("public IPC setup failed")
	}
	defer publicRead.Close()
	defer publicWrite.Close()

	home, err := os.UserHomeDir()
	if err != nil {
		return result, err
	}

	cmd := exec.Command(
		"node",
		"--import", "tsx",
		"--input-type=module",
		"--eval", source,
	)

	cmd.Dir = filepath.Join(home, "Developer/kohaku-cli")
	cmd.ExtraFiles = []*os.File{secretRead, publicWrite}
	cmd.Stdout = io.Discard
	cmd.Stderr = io.Discard
	cmd.Env = append(os.Environ(), "NODE_OPTIONS=")

	if err := cmd.Start(); err != nil {
		return result, errors.New("Node process startup failed")
	}

	secretRead.Close()
	publicWrite.Close()

	// R3 expects two 32-byte inputs. Both originate from
	// this independently authenticated card session.
	payload := make([]byte, 64)
	copy(payload[:32], root[:])
	copy(payload[32:], root[:])

	n, writeErr := secretWrite.Write(payload)
	clear(payload)
	secretWrite.Close()

	raw, readErr := io.ReadAll(io.LimitReader(publicRead, 1024))
	publicRead.Close()

	waitErr := cmd.Wait()

	if writeErr != nil || n != 64 ||
		readErr != nil || waitErr != nil {
		clear(raw)
		return result, errors.New("SDK reconstruction failed")
	}

	err = json.Unmarshal(raw, &result)
	clear(raw)

	if err != nil ||
		result.Deposit == "" ||
		result.Withdrawal == "" {
		return result, errors.New("invalid public result")
	}

	return result, nil
}

// Executed only inside a separately launched OS process.
func TestR4Worker(t *testing.T) {
	if os.Getenv("KOHAKU_R4_WORKER") != "1" {
		return
	}

	root, err := acquire()
	if err != nil {
		t.Fatal("hardware authentication failed:", err)
	}
	defer clear(root[:])

	result, err := r4Compute(&root)
	if err != nil {
		t.Fatal(err)
	}

	// Descriptor 3 is an anonymous pipe back to the
	// parent. It never writes to disk or terminal.
	output := os.NewFile(3, "public-result")
	if output == nil {
		t.Fatal("parent IPC unavailable")
	}
	defer output.Close()

	if err := json.NewEncoder(output).Encode(result); err != nil {
		t.Fatal("public result transfer failed")
	}
}

func r4Launch(t *testing.T) r4PublicResult {
	t.Helper()

	readEnd, writeEnd, err := os.Pipe()
	if err != nil {
		t.Fatal(err)
	}
	defer readEnd.Close()
	defer writeEnd.Close()

	cmd := exec.Command(
		os.Args[0],
		"-test.run=^TestR4Worker$",
		"-test.count=1",
	)

	cmd.Env = append(os.Environ(), "KOHAKU_R4_WORKER=1")
	cmd.ExtraFiles = []*os.File{writeEnd}
	cmd.Stdout = io.Discard
	cmd.Stderr = os.Stderr

	if err := cmd.Start(); err != nil {
		t.Fatal("worker startup failed:", err)
	}

	writeEnd.Close()

	raw, readErr := io.ReadAll(io.LimitReader(readEnd, 1024))
	readEnd.Close()

	waitErr := cmd.Wait()

	if readErr != nil || waitErr != nil {
		clear(raw)
		t.Fatal("independent hardware process failed")
	}

	var result r4PublicResult
	err = json.Unmarshal(bytes.TrimSpace(raw), &result)
	clear(raw)

	if err != nil ||
		result.Deposit == "" ||
		result.Withdrawal == "" {
		t.Fatal("invalid worker result")
	}

	return result
}

func TestR4ProcessRestart(t *testing.T) {
	if os.Getenv("KOHAKU_R4_WORKER") == "1" {
		return
	}

	fmt.Println("=== Cold start 1 ===")
	first := r4Launch(t)
	fmt.Println("PASS: First independent Go + Node process")

	fmt.Println("=== Cold start 2 ===")
	second := r4Launch(t)
	fmt.Println("PASS: Second independent Go + Node process")

	if first.Deposit != second.Deposit {
		t.Fatal("deposit precommitment mismatch")
	}
	fmt.Println("PASS: Deposit precommitment reconstructed")

	if first.Withdrawal != second.Withdrawal {
		t.Fatal("withdrawal precommitment mismatch")
	}
	fmt.Println("PASS: Withdrawal precommitment reconstructed")

	fmt.Println("PASS: V3-R4 cold-start recovery checkpoint")
}
