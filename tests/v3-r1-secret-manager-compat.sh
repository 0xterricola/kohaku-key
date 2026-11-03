#!/usr/bin/env bash
set -euo pipefail

cli="${KOHAKU_CLI_DIR:-$HOME/Developer/kohaku-cli}"

(
cd "$cli"

node --import tsx --input-type=module <<'JS'
import assert from "node:assert/strict";
import { createHmac, randomBytes } from "node:crypto";
import { SecretManager } from "@kohaku-eth/privacy-pools";

// Synthetic runtime-only material. No real card secrets.
const rootA = randomBytes(32);
const rootB = randomBytes(32);

function createManager(root) {
  return SecretManager({
    accountIndex: 0,
    host: {
      keystore: {
        async deriveAt(keyPath) {
          assert.ok(
            keyPath.startsWith("m/28784'/1'"),
            "Unexpected derivation path"
          );

          return "0x" + createHmac("sha256", root)
            .update("kohaku-key/v3/r1/synthetic-only/v1")
            .update("\0")
            .update(keyPath)
            .digest("hex");
        },
      },
    },
  });
}

try {
  const first = createManager(rootA);
  const restarted = createManager(rootA);
  const differentRoot = createManager(rootB);

  const context = {
    chainId: 11155111n,
    entrypointAddress:
      0x34A2068192b1297f2a7f85D7D8CdE66F8F0921cBn,
  };

  const deposit = {
    ...context,
    depositIndex: 0,
  };

  const withdrawal = {
    ...deposit,
    withdrawIndex: 1,
  };

  const d0 = await first.getDepositSecrets(deposit);
  const d0Again = await restarted.getDepositSecrets(deposit);

  assert.deepEqual(d0, d0Again);
  console.log("PASS: Deterministic deposit reconstruction");

  const initial = await first.getSecrets({
    ...deposit,
    withdrawIndex: 0,
  });

  assert.deepEqual(initial, d0);
  console.log("PASS: Initial note compatibility");

  const w1 = await first.getSecrets(withdrawal);
  const w1Again = await restarted.getSecrets(withdrawal);

  assert.deepEqual(w1, w1Again);
  assert.notEqual(w1.precommitment, d0.precommitment);
  console.log("PASS: Partial-withdrawal reconstruction");

  const d1 = await first.getDepositSecrets({
    ...context,
    depositIndex: 1,
  });

  assert.notEqual(d0.precommitment, d1.precommitment);
  console.log("PASS: Deposit-index separation");

  const otherChain = await first.getDepositSecrets({
    ...deposit,
    chainId: 1n,
  });

  assert.notEqual(d0.precommitment, otherChain.precommitment);
  console.log("PASS: Chain separation");

  const otherRoot = await differentRoot.getDepositSecrets(deposit);

  assert.notEqual(d0.precommitment, otherRoot.precommitment);
  console.log("PASS: Root-key separation");

  const signerA = await first.deriveEphemeralSigner(withdrawal);
  const signerB = await restarted.deriveEphemeralSigner(withdrawal);

  assert.equal(signerA, signerB);
  console.log("PASS: Ephemeral signer reproducibility");

  console.log("PASS: Seven R1 compatibility checks");
} finally {
  rootA.fill(0);
  rootB.fill(0);
}
JS
)
