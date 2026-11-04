import assert from "node:assert/strict";
import { createHmac, randomBytes } from "node:crypto";
import { readFileSync, readSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import { poseidon } from "maci-crypto/build/ts/hashing.js";
import { encodePacked, keccak256 } from "viem";
import {
  PrivacyPoolsV1Protocol,
  SecretManager,
} from "@kohaku-eth/privacy-pools";

const chainId = 11155111n;
const entrypointAddress =
  0x34A2068192b1297f2a7f85D7D8CdE66F8F0921cBn;
const pool =
  0x644d5a2554d36e27509254F32ccfeBe8cd58861fn;
const asset =
  BigInt("0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE");

const FIELD =
  21888242871839275222246405745257275088548364400416034343698204186575808495617n;

const domain =
  "kohaku-key/v3-r3/privacy-pools-v1/deriveAt";
const refusal = "R5E1B_ONCHAIN_ROOT_NOT_VERIFIED";
const hex = n => `0x${n.toString(16)}`;
const addressHex = n =>
  `0x${n.toString(16).padStart(40, "0")}`;

const storageKey =
  `privacy-pool-state-${chainId}-${entrypointAddress}`;

const { formatCredentialId, sdkCoordinates } = await import(
  pathToFileURL(join(
    join(process.env.HOME, "Developer/kohaku-key"),
    "experiments/v3-r5e3-credential-ids.mjs"
  )).href
);

const snapshots = JSON.parse(readFileSync(
  "src/utils/ppv1-sepolia-state.json", "utf8"
));

const original = snapshots[storageKey];
assert.ok(original);

const snapshotHead = BigInt(
  original.sync.lastSyncedBlock
);

assert.equal(original.deposits.depositsTuples.length, 1153);
assert.equal(original.withdrawals.withdrawalsTuples.length, 750);

const scope = BigInt(keccak256(encodePacked(
  ["address", "uint256", "address"],
  [addressHex(pool), chainId, addressHex(asset)]
))) % FIELD;

// Hypothetical synthetic pool nonce; not an on-chain event.
const label = BigInt(keccak256(encodePacked(
  ["uint256", "uint256"],
  [scope, 1000000n]
))) % FIELD;

// Authenticated Keycard sessions supply roots through FD3.
const input = Buffer.alloc(64);
const rootA = Buffer.alloc(32);
const rootB = Buffer.alloc(32);
const rootWrong = randomBytes(32);

let offset = 0;
while (offset < input.length) {
  const count = readSync(
    3, input, offset, input.length - offset, null
  );
  assert.ok(count > 0, "Incomplete hardware IPC");
  offset += count;
}

input.copy(rootA, 0, 0, 32);
input.copy(rootB, 0, 32, 64);
input.fill(0);

assert.ok(
  rootA.equals(rootB),
  "Physical card session roots differ"
);

assert.ok(!rootA.equals(rootWrong));

console.log("PASS: Two independent hardware roots match");

function makeKeystore(root) {
  let calls = 0;

  return {
    get calls() { return calls; },

    async deriveAt(keyPath) {
      assert.match(
        keyPath,
        /^m\/28784'\/1'(?:\/[0-9]+')+$/
      );

      calls++;

      return "0x" + createHmac("sha256", root)
        .update(domain)
        .update("\0")
        .update(keyPath)
        .digest("hex");
    },
  };
}

function makeManager(keystore) {
  return SecretManager({
    host: { keystore },
    accountIndex: 0,
  });
}

const dataService = {
  async getChainId() { return chainId; },
  async getBlockNumber() { return snapshotHead; },

  async getEntrypointEvents({ fromBlock, toBlock }) {
    return {
      fromBlock, toBlock,
      EntrypointDeposited: [],
      RootUpdated: [],
      PoolRegistered: [],
      PoolWindDown: [],
    };
  },

  async getPoolEvents({ fromBlock, toBlock }) {
    return {
      fromBlock, toBlock,
      PoolDeposited: [],
      Withdrawn: [],
      Ragequit: [],
      LeafInserted: [],
    };
  },

  async getAsset(address) {
    return {
      address,
      name: "Offline Fixture",
      symbol: "TEST",
      decimals: 18,
    };
  },

  async getBlockTimestamp() { return 1700000000n; },
  async getLatestBlockTimestamp() { return 1700000000n; },

  async getPoolStateRoot() {
    throw new Error(refusal);
  },

  async getEntrypointLatestRoot() {
    throw new Error(refusal);
  },
};

async function main() {
  console.log("=== R5-E4B physical sparse recovery ===");

  const keystoreA = makeKeystore(rootA);
  const keystoreB = makeKeystore(rootB);
  const keystoreWrong = makeKeystore(rootWrong);

  const credentialId = formatCredentialId({
    chainId,
    entrypointAddress,
    accountIndex: 0,
    depositIndex: 17,
    role: "deposit",
    secretIndex: 0,
  });

  const coordinates = sdkCoordinates(credentialId, {
    chainId,
    entrypointAddress,
    accountIndex: 0,
  });

  assert.equal(coordinates.depositIndex, 17);

  assert.throws(() => sdkCoordinates(credentialId, {
    chainId: 1n,
    entrypointAddress,
    accountIndex: 0,
  }), /context mismatch/);

  console.log("PASS: Credential ID resolves to deposit 17");
  console.log("PASS: Incorrect chain rejected");

  const owned = await makeManager(keystoreA)
    .getDepositSecrets(coordinates);

  const wrong = await makeManager(keystoreWrong)
    .getDepositSecrets(coordinates);

  assert.notEqual(
    owned.precommitment,
    wrong.precommitment
  );

  const value = 100000000000000000n;
  const commitment = poseidon([
    value, label, owned.precommitment
  ]);

  assert.equal(
    commitment,
    poseidon([value, label, owned.precommitment])
  );

  assert.notEqual(
    commitment,
    poseidon([value, label, wrong.precommitment])
  );

  console.log("PASS: R3 credential roots are isolated");
  console.log("PASS: Poseidon commitment derived");

  // All modifications remain in memory.
  const fixture = structuredClone(original);

  assert.ok(
    !fixture.deposits.depositsTuples.some(
      ([key]) => BigInt(key) === owned.precommitment
    ),
    "Synthetic precommitment collides with real history"
  );

  assert.ok(
    !fixture.entrypointDeposits.entrypointDepositsTuples
      .some(([key]) => BigInt(key) === commitment),
    "Synthetic commitment collides with real history"
  );

  const syntheticTx = `0x${"ee".repeat(32)}`;
  const depositor = addressHex(0x5678n);
  const poolAddress = addressHex(pool);

  const deposit = {
    ...fixture.deposits.depositsTuples[0][1],
    depositor,
    commitment: hex(commitment),
    label: hex(label),
    value: hex(value),
    precommitment: hex(owned.precommitment),
    blockNumber: hex(snapshotHead),
    transactionHash: syntheticTx,
    pool: poolAddress,
  };

  const entrypointDeposit = {
    ...fixture.entrypointDeposits.entrypointDepositsTuples[0][1],
    depositor,
    poolAddress,
    commitment: hex(commitment),
    value: hex(value),
    blockNumber: hex(snapshotHead),
    transactionHash: syntheticTx,
  };

  fixture.deposits.depositsTuples.push([
    hex(owned.precommitment),
    deposit,
  ]);

  fixture.entrypointDeposits.entrypointDepositsTuples.push([
    hex(commitment),
    entrypointDeposit,
  ]);

  assert.equal(fixture.deposits.depositsTuples.length, 1154);
  assert.equal(
    fixture.entrypointDeposits.entrypointDepositsTuples.length,
    1154
  );
  assert.equal(original.deposits.depositsTuples.length, 1153);

  // No synthetic Merkle leaf is added. This tests discovery,
  // not on-chain inclusion, root verification, or spending.
  console.log("PASS: Synthetic deposit injected in memory");
  console.log("PASS: Original public snapshot preserved");

  function freshProtocol(keystore, explicitId = false) {
    return new PrivacyPoolsV1Protocol(
      { keystore, network: {} },
      {
        accountIndex: 0,
        entrypoint: {
          address: entrypointAddress,
          deploymentBlock: 8587019n,
        },

        initialState: async () => {
          const state = structuredClone(fixture);

          if (explicitId) {
            const secret = await makeManager(keystore)
              .getDepositSecrets(coordinates);

            const matched = state.deposits.depositsTuples
              .some(([key]) =>
                BigInt(key) === secret.precommitment
              );

            if (matched) {
              // Explicit discovery: hydrate only this verified
              // credential in volatile SDK state.
              state.userSecrets = {
                recordsByPrecommitment: [[
                  hex(secret.precommitment),
                  {
                    depositIndex: coordinates.depositIndex,
                    noteSecrets: [{
                      noteIndex: 0,
                      nullifier: hex(secret.nullifier),
                      salt: hex(secret.salt),
                      precommitment: hex(secret.precommitment),
                      nullifierHash: hex(secret.nullifierHash),
                    }],
                  },
                ]],
              };
            }
          }

          return { [storageKey]: state };
        },

        secretManager: () => makeManager(keystore),
        dataService,

        aspServiceFactory: () => ({
          async getAspTree() { return []; },
        }),

        relayerClientFactory: () => ({}),
        proverFactory: () => ({}),
        relayersList: {},
      }
    );
  }

  async function recover(keystore, expected, explicitId = false) {
    const protocol = freshProtocol(keystore, explicitId);

    let refused = false;

    try {
      await protocol.sync();
    } catch (error) {
      assert.ok(
        String(error?.message ?? error).includes(refusal),
        "Unexpected sync failure"
      );
      refused = true;
    }

    assert.ok(refused, "Offline root verification not refused");

    const notes = await protocol.notes(
      undefined, true, { sync: false }
    );

    assert.equal(
      notes.length, expected,
      "Unexpected recovered note count"
    );

    if (expected === 1) {
      const note = notes[0];

      assert.equal(note.deposit, 17);
      assert.equal(note.withdraw, 0);
      assert.equal(note.precommitment, owned.precommitment);
      assert.equal(note.commitment, commitment);
      assert.equal(note.label, label);
      assert.equal(note.value, value);
      assert.equal(note.balance, value);
      assert.equal(note.assetAddress, asset);
    }

    const dump = await protocol.stateManager.dumpState();
    assert.ok(dump[storageKey]);

    assert.ok(
      !Object.hasOwn(dump[storageKey], "userSecrets"),
      "Private secrets leaked into public state"
    );

    return protocol;
  }

  // Existing sequential discovery must miss sparse index 17.
  await recover(keystoreA, 0);
  console.log("PASS: Automatic discovery misses sparse index");

  // An explicit identifier hydrates its matching credential.
  await recover(keystoreA, 1, true);
  assert.ok(keystoreA.calls > 0);

  console.log("PASS: SDK recovered owned synthetic note");
  console.log("PASS: Commitment, label and balance match");

  await recover(keystoreWrong, 0, true);
  assert.ok(keystoreWrong.calls > 0);

  console.log("PASS: Wrong root recovers zero notes");

  await recover(keystoreB, 1, true);
  assert.ok(keystoreB.calls > 0);
  console.log("PASS: Second physical session recovers index 17");

  await recover(makeKeystore(rootA), 1, true);

  console.log("PASS: Fresh SDK instance recovers same note");
  console.log("PASS: Offline root verification refused");
  console.log("PASS: Public SDK state excludes secrets");
  console.log("PASS: R5-E4B physical sparse recovery checkpoint");
}

try {
  await main();
} finally {
  rootA.fill(0);
  rootB.fill(0);
  rootWrong.fill(0);
}
