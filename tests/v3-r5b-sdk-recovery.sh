#!/usr/bin/env bash
set -euo pipefail

cli="${KOHAKU_CLI_DIR:-$HOME/Developer/kohaku-cli}"

(
cd "$cli"

node --import tsx --input-type=module <<'JS'
import assert from "node:assert/strict";
import { createHmac, randomBytes } from "node:crypto";
import {
  PrivacyPoolsV1Protocol,
  SecretManager,
} from "@kohaku-eth/privacy-pools";

const root = randomBytes(32);
const domain = "kohaku-key/v3-r3/privacy-pools-v1/deriveAt";

const chainId = 11155111n;
const entrypointAddress =
  0x34A2068192b1297f2a7f85D7D8CdE66F8F0921cBn;
const pool = 0x1234n;
const asset = 0x2222n;

const keystore = {
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
};

const context = { chainId, entrypointAddress };

const makeSecrets = () => SecretManager({
  host: { keystore },
  accountIndex: 0,
});

const inRange = (items, start, end) =>
  items.filter(e =>
    e.blockNumber >= start &&
    e.blockNumber <= end
  );

try {
  const manager = makeSecrets();

  const deposit0 = await manager.getDepositSecrets({
    ...context,
    depositIndex: 0,
  });

  const deposit1 = await manager.getDepositSecrets({
    ...context,
    depositIndex: 1,
  });

  const withdrawal1 = await manager.getSecrets({
    ...context,
    depositIndex: 0,
    withdrawIndex: 1,
  });

  assert.notEqual(
    deposit0.nullifierHash,
    withdrawal1.nullifierHash
  );

  const registration = {
    pool,
    asset,
    scope: 777n,
    blockNumber: 100n,
    transactionHash: 1000n,
  };

  const deposits = [
    {
      depositor: 0x5678n,
      commitment: 901n,
      label: 651n,
      precommitment: deposit0.precommitment,
      value: 1000n,
      blockNumber: 101n,
      transactionHash: 1001n,
      logIndex: 0,
    },
    {
      depositor: 0x9999n,
      commitment: 999n,
      label: 699n,
      precommitment: 999999n,
      value: 4000n,
      blockNumber: 102n,
      transactionHash: 1002n,
      logIndex: 0,
    },
    {
      depositor: 0x5678n,
      commitment: 902n,
      label: 652n,
      precommitment: deposit1.precommitment,
      value: 600n,
      blockNumber: 103n,
      transactionHash: 1003n,
      logIndex: 0,
    },
  ];

  const entrypointDeposits = deposits.map(e => ({
    depositor: e.depositor,
    poolAddress: pool,
    commitment: e.commitment,
    blockNumber: e.blockNumber,
    transactionHash: e.transactionHash,
    logIndex: 1,
  }));

  // Intentionally unordered to exercise event processing.
  const withdrawals = [
    {
      spentNullifier: withdrawal1.nullifierHash,
      commitment: 904n,
      value: 300n,
      blockNumber: 108n,
      transactionHash: 1008n,
      logIndex: 0,
    },
    {
      spentNullifier: 888888n,
      commitment: 999n,
      value: 50n,
      blockNumber: 106n,
      transactionHash: 1006n,
      logIndex: 0,
    },
    {
      spentNullifier: deposit0.nullifierHash,
      commitment: 903n,
      value: 200n,
      blockNumber: 105n,
      transactionHash: 1005n,
      logIndex: 0,
    },
  ];

  const dataService = {
    async getChainId() {
      return chainId;
    },

    async getBlockNumber() {
      return 110n;
    },

    async getEntrypointEvents({
      address, fromBlock, toBlock,
    }) {
      assert.equal(address, entrypointAddress);

      return {
        fromBlock,
        toBlock,
        PoolRegistered: inRange(
          [registration], fromBlock, toBlock
        ),
        EntrypointDeposited: inRange(
          entrypointDeposits, fromBlock, toBlock
        ),
        RootUpdated: [],
        PoolWindDown: [],
      };
    },

    async getPoolEvents({
      address, fromBlock, toBlock,
    }) {
      assert.equal(address, pool);

      return {
        fromBlock,
        toBlock,
        PoolDeposited: inRange(
          deposits, fromBlock, toBlock
        ),
        Withdrawn: inRange(
          withdrawals, fromBlock, toBlock
        ),
        Ragequit: [],
        LeafInserted: [],
      };
    },

    async getAsset(address) {
      assert.equal(address, asset);

      return {
        address: asset,
        name: "Synthetic Token",
        symbol: "TEST",
        decimals: 18,
      };
    },

    async getBlockTimestamp() {
      return 1700000000n;
    },

    async getLatestBlockTimestamp() {
      return 1700000000n;
    },
  };

  function freshProtocol() {
    return new PrivacyPoolsV1Protocol(
      { keystore, network: {} },
      {
        entrypoint: {
          address: entrypointAddress,
          deploymentBlock: 100n,
        },
        accountIndex: 0,
        secretManager: () => makeSecrets(),
        dataService,
        aspServiceFactory: () => ({
          async getAspTree() {
            return [];
          },
        }),
        relayerClientFactory: () => ({}),
        proverFactory: () => ({}),
        relayersList: {},
      }
    );
  }

  async function recover() {
    const protocol = freshProtocol();

    await protocol.sync();

    const notes = await protocol.notes(
      undefined, true, { sync: false }
    );

    assert.equal(notes.length, 2);

    const byIndex = new Map(
      notes.map(note => [note.deposit, note])
    );

    assert.equal(byIndex.get(0)?.balance, 500n);
    assert.equal(byIndex.get(0)?.withdraw, 2);
    assert.equal(
      byIndex.get(0)?.precommitment,
      deposit0.precommitment
    );

    assert.equal(byIndex.get(1)?.balance, 600n);
    assert.equal(byIndex.get(1)?.withdraw, 0);
    assert.equal(
      byIndex.get(1)?.precommitment,
      deposit1.precommitment
    );

    assert.equal(
      notes.reduce((sum, note) => sum + note.balance, 0n),
      1100n
    );

    return protocol;
  }

  const first = await recover();
  console.log(
    "PASS: SDK reconstructed two partial withdrawals"
  );
  console.log(
    "PASS: Untouched deposit and remaining balances correct"
  );
  console.log("PASS: Unrelated deposit and spend excluded");

  const history = await first.history(
    undefined, { sync: false }
  );

  assert.equal(
    history.length,
    4,
    `Expected 2 deposits + 2 owned withdrawals; got ${history.length}`
  );
  console.log("PASS: SDK recovered four history events");

  await recover();
  console.log(
    "PASS: Fresh SDK instance reconstructed balances"
  );

  console.log("PASS: V3-R5-B3B SDK recovery checkpoint");
} finally {
  root.fill(0);
}
JS
)
