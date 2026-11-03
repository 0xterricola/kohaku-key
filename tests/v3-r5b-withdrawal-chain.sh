#!/usr/bin/env bash
set -euo pipefail

cli="${KOHAKU_CLI_DIR:-$HOME/Developer/kohaku-cli}"

(
cd "$cli"

node --import tsx --input-type=module <<'JS'
import assert from "node:assert/strict";
import { createHmac, randomBytes } from "node:crypto";
import { SecretManager } from "@kohaku-eth/privacy-pools";

const root = randomBytes(32);
const domain = "kohaku-key/v3-r3/privacy-pools-v1/deriveAt";

function manager() {
  return SecretManager({
    accountIndex: 0,
    host: {
      keystore: {
        async deriveAt(keyPath) {
          assert.match(
            keyPath,
            /^m\/28784'\/1'(?:\/[0-9]+')+$/
          );

          return "0x" + createHmac("sha256", root)
            .update(domain)
            .update("\0")
            .update(keyPath)
            .digest("hex");
        },
      },
    },
  });
}

const context = {
  chainId: 11155111n,
  entrypointAddress:
    0x34A2068192b1297f2a7f85D7D8CdE66F8F0921cBn,
};

function deposit(m, depositIndex) {
  return m.getDepositSecrets({ ...context, depositIndex });
}

function secrets(m, depositIndex, withdrawIndex) {
  return m.getSecrets({
    ...context,
    depositIndex,
    withdrawIndex,
  });
}

function validateCoverage(spans, start, tip) {
  let next = start;

  for (const [lo, hi] of [...spans].sort(
    (a, b) => a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0
  )) {
    assert.ok(lo <= next, "Uncovered blockchain range");
    assert.ok(hi >= lo, "Invalid scan range");

    if (hi >= next) next = hi + 1n;
  }

  assert.ok(next > tip, "Incomplete blockchain coverage");
}

async function discover(m, deposits, withdrawals, spans, limit = 6) {
  validateCoverage(spans, 100n, 110n);

  const discovered = [];

  for (let depositIndex = 0; depositIndex <= 3; depositIndex++) {
    const candidate = await deposit(m, depositIndex);

    const matched = deposits.filter(
      e => e.precommitment === candidate.precommitment
    );

    assert.ok(matched.length <= 1, "Duplicate deposit");

    if (!matched.length) continue;

    const history = [];
    const depositBlock = matched[0].blockNumber;

    for (let withdrawIndex = 0; withdrawIndex < limit; withdrawIndex++) {
      const current = await secrets(
        m, depositIndex, withdrawIndex
      );

      const matches = withdrawals.filter(
        e => e.spentNullifier === current.nullifierHash
      );

      assert.ok(matches.length <= 1, "Duplicate nullifier spend");

      if (!matches.length) {
        discovered.push({
          depositIndex,
          spentCount: history.length,
          nextWithdrawIndex: withdrawIndex,
        });
        break;
      }

      const previousBlock = history.length
        ? history[history.length - 1]
        : depositBlock;

      assert.ok(
        matches[0].blockNumber > previousBlock,
        "Invalid withdrawal ordering"
      );

      history.push(matches[0].blockNumber);
    }

    if (
      !discovered.some(x => x.depositIndex === depositIndex)
    ) {
      throw new Error("Withdrawal search limit exhausted");
    }
  }

  return discovered.sort(
    (a, b) => a.depositIndex - b.depositIndex
  );
}

try {
  const original = manager();
  const restarted = manager();

  const d0 = await deposit(original, 0);
  const d2 = await deposit(original, 2);

  const w0 = await secrets(original, 0, 0);
  const w1 = await secrets(original, 0, 1);
  const w2 = await secrets(original, 0, 2);

  assert.notEqual(w0.nullifierHash, w1.nullifierHash);
  assert.notEqual(w1.nullifierHash, w2.nullifierHash);
  console.log("PASS: Distinct withdrawal-chain nullifiers");

  const deposits = [
    { precommitment: d2.precommitment, blockNumber: 103n },
    { precommitment: 999999n, blockNumber: 102n },
    { precommitment: d0.precommitment, blockNumber: 101n },
  ];

  // Deliberately unordered synthetic public events.
  const withdrawals = [
    { spentNullifier: w1.nullifierHash, blockNumber: 107n },
    { spentNullifier: 888888n, blockNumber: 105n },
    { spentNullifier: w0.nullifierHash, blockNumber: 104n },
  ];

  const fullCoverage = [[100n, 110n]];

  const found = await discover(
    restarted, deposits, withdrawals, fullCoverage
  );

  assert.deepEqual(found, [
    {
      depositIndex: 0,
      spentCount: 2,
      nextWithdrawIndex: 2,
    },
    {
      depositIndex: 2,
      spentCount: 0,
      nextWithdrawIndex: 0,
    },
  ]);
  console.log("PASS: Two successive withdrawals reconstructed");
  console.log("PASS: Untouched deposit retained");
  console.log("PASS: Unrelated events excluded");
  console.log("PASS: Deposit-index gaps handled");

  await assert.rejects(
    discover(
      restarted, deposits, withdrawals,
      [[100n, 102n], [104n, 110n]]
    ),
    /Uncovered blockchain range/
  );
  console.log("PASS: Blockchain scan gaps rejected");

  await assert.rejects(
    discover(
      restarted, deposits, withdrawals,
      [[101n, 110n]]
    ),
    /Uncovered blockchain range/
  );
  console.log("PASS: Missing early history rejected");

  await assert.rejects(
    discover(
      restarted, deposits, withdrawals,
      [[100n, 105n]]
    ),
    /Incomplete blockchain coverage/
  );
  console.log("PASS: Incomplete chain tip rejected");

  await assert.rejects(
    discover(
      restarted,
      deposits,
      [...withdrawals, { ...withdrawals[2], blockNumber: 108n }],
      fullCoverage
    ),
    /Duplicate nullifier spend/
  );
  console.log("PASS: Duplicate nullifier spend rejected");

  await assert.rejects(
    discover(
      restarted, deposits, withdrawals, fullCoverage, 2
    ),
    /Withdrawal search limit exhausted/
  );
  console.log("PASS: Exhausted withdrawal search rejected");

  console.log("PASS: V3-R5-B2 withdrawal-chain checkpoint");
} finally {
  root.fill(0);
}
JS
)
