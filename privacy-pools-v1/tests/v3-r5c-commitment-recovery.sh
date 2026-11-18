#!/usr/bin/env bash
set -euo pipefail

cli="${KOHAKU_CLI_DIR:-$HOME/Developer/kohaku-cli}"

(
cd "$cli"

node --import tsx --input-type=module <<'JS'
import assert from "node:assert/strict";
import { createHmac, randomBytes } from "node:crypto";
import { poseidon } from "maci-crypto/build/ts/hashing.js";
import { encodePacked, keccak256 } from "viem";
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

const FIELD =
  21888242871839275222246405745257275088548364400416034343698204186575808495617n;

const addressHex = value =>
  `0x${value.toString(16).padStart(40, "0")}`;

// Matches State.sol:
// SCOPE = keccak256(pool, chainId, asset) % FIELD.
const scope = BigInt(keccak256(encodePacked(
  ["address", "uint256", "address"],
  [addressHex(pool), chainId, addressHex(asset)]
))) % FIELD;

// Matches PrivacyPool.sol:
// label = keccak256(SCOPE, ++nonce) % FIELD.
function labelAt(nonce) {
  return BigInt(keccak256(encodePacked(
    ["uint256", "uint256"],
    [scope, BigInt(nonce)]
  ))) % FIELD;
}

// Matches PoseidonT4.hash([value, label, precommitment])
// and the v1 CommitmentHasher circuit.
function commitmentFor(value, label, precommitment) {
  return poseidon([value, label, precommitment]);
}

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

  const withdrawal2 = await manager.getSecrets({
    ...context,
    depositIndex: 0,
    withdrawIndex: 2,
  });

  assert.notEqual(
    deposit0.nullifierHash,
    withdrawal1.nullifierHash
  );
  assert.notEqual(
    withdrawal1.nullifierHash,
    withdrawal2.nullifierHash
  );

  assert.notEqual(labelAt(1), labelAt(2));
  assert.notEqual(labelAt(2), labelAt(3));
  console.log("PASS: Pool scope and nonce-derived labels");

  const registration = {
    pool,
    asset,
    scope,
    blockNumber: 100n,
    transactionHash: 1000n,
  };

  const deposits = [
    {
      depositor: 0x5678n,
      commitment: commitmentFor(
        1000n, labelAt(1), deposit0.precommitment
      ),
      label: labelAt(1),
      precommitment: deposit0.precommitment,
      value: 1000n,
      blockNumber: 101n,
      transactionHash: 1001n,
      logIndex: 0,
    },
    {
      depositor: 0x9999n,
      commitment: commitmentFor(
        4000n, labelAt(2), 999999n
      ),
      label: labelAt(2),
      precommitment: 999999n,
      value: 4000n,
      blockNumber: 102n,
      transactionHash: 1002n,
      logIndex: 0,
    },
    {
      depositor: 0x5678n,
      commitment: commitmentFor(
        600n, labelAt(3), deposit1.precommitment
      ),
      label: labelAt(3),
      precommitment: deposit1.precommitment,
      value: 600n,
      blockNumber: 103n,
      transactionHash: 1003n,
      logIndex: 0,
    },
  ];

  assert.equal(deposits[0].label, labelAt(1));
  assert.equal(deposits[2].label, labelAt(3));
  assert.notEqual(
    deposits[0].commitment,
    commitmentFor(1000n, labelAt(2), deposit0.precommitment)
  );

  console.log("PASS: Protocol-derived deposit commitments");

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
      commitment: commitmentFor(
        500n, labelAt(1), withdrawal2.precommitment
      ),
      value: 300n,
      blockNumber: 108n,
      transactionHash: 1008n,
      logIndex: 0,
    },
    {
      spentNullifier: 888888n,
      commitment: commitmentFor(
        3950n, labelAt(2), 999999n
      ),
      value: 50n,
      blockNumber: 106n,
      transactionHash: 1006n,
      logIndex: 0,
    },
    {
      spentNullifier: deposit0.nullifierHash,
      commitment: commitmentFor(
        800n, labelAt(1), withdrawal1.precommitment
      ),
      value: 200n,
      blockNumber: 105n,
      transactionHash: 1005n,
      logIndex: 0,
    },
  ];

  assert.notEqual(
    withdrawals[0].commitment,
    withdrawals[2].commitment
  );
  assert.notEqual(
    withdrawals[0].spentNullifier,
    withdrawals[2].spentNullifier
  );
  console.log("PASS: Replacement-note commitment lineage");

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

  console.log("PASS: V3-R5-C1 cryptographic commitment recovery");
} finally {
  root.fill(0);
}
JS
)
