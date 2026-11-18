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

const manager = SecretManager({
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

const context = {
  chainId: 11155111n,
  entrypointAddress:
    0x34A2068192b1297f2a7f85D7D8CdE66F8F0921cBn,
};

const pool = 0x1234n;

async function deposit(index, overrides = {}) {
  return manager.getDepositSecrets({
    ...context,
    depositIndex: index,
    ...overrides,
  });
}

async function withdrawal(index, withdrawIndex) {
  return manager.getSecrets({
    ...context,
    depositIndex: index,
    withdrawIndex,
  });
}

function event(precommitment, blockNumber) {
  return {
    depositor: 0x5678n,
    commitment: 987n,
    label: 654n,
    precommitment,
    value: 1000n,
    blockNumber,
    transactionHash: blockNumber + 1000n,
  };
}

try {
  const owned0 = await deposit(0);
  const owned2 = await deposit(2);
  const wrongChain = await deposit(0, { chainId: 1n });
  const spent0 = await withdrawal(0, 0);

  const deposits = [
    event(wrongChain.precommitment, 101n),
    event(owned2.precommitment, 103n),
    event(999999n, 104n),
    event(owned0.precommitment, 102n),
  ];

  const withdrawals = [
    {
      spentNullifier: 999999n,
      commitment: 888n,
      value: 100n,
      blockNumber: 105n,
      transactionHash: 1105n,
    },
    {
      spentNullifier: spent0.nullifierHash,
      commitment: 777n,
      value: 200n,
      blockNumber: 106n,
      transactionHash: 1106n,
    },
  ];

  // Synthetic provider follows the SDK's grouped event interface.
  const getPoolEvents = async ({
    address, events, fromBlock, toBlock,
  }) => {
    assert.equal(address, pool);

    const wanted = new Set(
      Array.isArray(events) ? events : [events]
    );

    const inRange = e =>
      e.blockNumber >= fromBlock &&
      (toBlock === undefined || e.blockNumber <= toBlock);

    return {
      fromBlock,
      toBlock: toBlock ?? 106n,
      PoolDeposited: wanted.has("PoolDeposited")
        ? deposits.filter(inRange) : [],
      Withdrawn: wanted.has("Withdrawn")
        ? withdrawals.filter(inRange) : [],
    };
  };

  async function discover(fromBlock, maxIndex) {
    const logs = await getPoolEvents({
      address: pool,
      events: ["PoolDeposited", "Withdrawn"],
      fromBlock,
      toBlock: 106n,
    });

    const found = [];

    for (let index = 0; index <= maxIndex; index++) {
      const candidate = await deposit(index);

      const matched = logs.PoolDeposited.find(
        e => e.precommitment === candidate.precommitment
      );

      if (matched) {
        const initial = await withdrawal(index, 0);

        found.push({
          index,
          blockNumber: matched.blockNumber,
          spent: logs.Withdrawn.some(
            e => e.spentNullifier === initial.nullifierHash
          ),
        });
      }
    }

    return found.sort((a, b) => a.index - b.index);
  }

  const recovered = await discover(100n, 3);

  assert.deepEqual(
    recovered.map(x => x.index),
    [0, 2]
  );
  console.log("PASS: Owned deposits rediscovered");

  assert.equal(recovered.length, 2);
  console.log("PASS: Unrelated deposits excluded");

  assert.equal(recovered[0].spent, true);
  assert.equal(recovered[1].spent, false);
  console.log("PASS: Withdrawal nullifier matching");

  assert.deepEqual(
    recovered.map(x => x.index),
    [0, 2]
  );
  console.log("PASS: Deposit-index gaps handled");

  const incomplete = await discover(103n, 3);
  assert.deepEqual(
    incomplete.map(x => x.index),
    [2]
  );
  console.log("PASS: Missing scan history detected");

  assert.notEqual(
    owned0.precommitment,
    wrongChain.precommitment
  );
  console.log("PASS: Chain-separated decoy excluded");

  console.log("PASS: V3-R5-B1 offline event matching");
} finally {
  root.fill(0);
}
JS
)
