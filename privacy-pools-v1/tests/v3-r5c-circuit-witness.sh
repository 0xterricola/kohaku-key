#!/usr/bin/env bash
set -euo pipefail

cli="${KOHAKU_CLI_DIR:-$HOME/Developer/kohaku-cli}"

echo "=== R5-C3 circuit witnesses and proof ==="

proof_json="$(
  cd "$cli"

  node --import tsx --input-type=module <<'JS'
import assert from "node:assert/strict";
import * as snarkjs from "snarkjs";
import { resolve } from "node:path";
import { poseidon } from "maci-crypto/build/ts/hashing.js";
import { encodePacked, keccak256 } from "viem";

const watchdog = setTimeout(() => {
  console.error("FAIL: Circuit proving timeout");
  process.exit(124);
}, 120000);

const FIELD =
  21888242871839275222246405745257275088548364400416034343698204186575808495617n;

const artifacts = resolve(
  "node_modules/@fatsolutions/privacy-pools-core-circuits/artifacts"
);

const wasm = resolve(artifacts, "commitment.wasm");
const zkey = resolve(artifacts, "commitment.zkey");

const scope = BigInt(keccak256(encodePacked(
  ["address", "uint256", "address"],
  [
    "0x0000000000000000000000000000000000001234",
    11155111n,
    "0x0000000000000000000000000000000000002222",
  ]
))) % FIELD;

const label = BigInt(keccak256(encodePacked(
  ["uint256", "uint256"],
  [scope, 1n]
))) % FIELD;

// Explicitly synthetic test fixtures.
// No physical Keycard or real credential material.
const fixtures = [
  {
    name: "original deposit",
    value: 1000n,
    nullifier: 123n,
    secret: 456n,
  },
  {
    name: "first replacement",
    value: 800n,
    nullifier: 789n,
    secret: 987n,
  },
  {
    name: "second replacement",
    value: 500n,
    nullifier: 321n,
    secret: 654n,
  },
];

async function main() {
  const commitments = [];
  let proofPayload;

  for (const [index, fixture] of fixtures.entries()) {
    const { value, nullifier, secret } = fixture;

    const precommitment = poseidon([nullifier, secret]);

    const commitment = poseidon([
      value,
      label,
      precommitment,
    ]);

    const nullifierHash = poseidon([nullifier]);

    const witnessHandle = { type: "mem" };

    await snarkjs.wtns.calculate({
      value: value.toString(),
      label: label.toString(),
      nullifier: nullifier.toString(),
      secret: secret.toString(),
    }, wasm, witnessHandle);

    const witness = await snarkjs.wtns.exportJson(
      witnessHandle
    );

    assert.equal(BigInt(witness[0]), 1n);
    assert.equal(BigInt(witness[1]), commitment);
    assert.equal(BigInt(witness[2]), nullifierHash);

    commitments.push(commitment);

    console.error(
      `PASS: Circuit witness — ${fixture.name}`
    );

    if (index === 0) {
      const { proof, publicSignals } =
        await snarkjs.groth16.prove(
          zkey,
          witnessHandle,
          undefined,
          { singleThread: true }
        );

      assert.equal(publicSignals.length, 4);

      assert.deepEqual(
        publicSignals.map(BigInt),
        witness.slice(1, 5).map(BigInt)
      );

      assert.equal(
        BigInt(publicSignals[0]), commitment
      );

      assert.equal(
        BigInt(publicSignals[1]), nullifierHash
      );

      proofPayload = { proof, publicSignals };

      console.error("PASS: Groth16 proof generated");
      console.error("PASS: Four public signals match witness");
    }
  }

  assert.equal(new Set(commitments).size, 3);
  assert.ok(proofPayload);

  console.error(
    "PASS: Three distinct commitment states"
  );

  // Emit only the proof and public signals from synthetic
  // fixtures; never witness secrets.
  await new Promise(resolve => {
    process.stdout.write(
      JSON.stringify(proofPayload) + "\n",
      resolve
    );
  });
}

main().then(
  () => {
    clearTimeout(watchdog);
    process.exit(0);
  },
  error => {
    console.error("FAIL:", error.stack ?? error);
    clearTimeout(watchdog);
    process.exit(1);
  }
);
JS
)"

echo
echo "=== R5-C3 independent proof verification ==="

(
  cd "$cli"

  SYNTHETIC_PROOF_JSON="$proof_json" \
  node --input-type=module <<'JS'
import assert from "node:assert/strict";
import * as snarkjs from "snarkjs";
import { resolve } from "node:path";

const watchdog = setTimeout(() => {
  console.error("FAIL: Proof verification timeout");
  process.exit(124);
}, 120000);

async function main() {
  const { proof, publicSignals } =
    JSON.parse(process.env.SYNTHETIC_PROOF_JSON);

  const zkey = resolve(
    "node_modules/@fatsolutions/privacy-pools-core-circuits/artifacts/commitment.zkey"
  );

  const verificationKey =
    await snarkjs.zKey.exportVerificationKey(zkey);

  assert.equal(verificationKey.protocol, "groth16");
  assert.equal(Number(verificationKey.nPublic), 4);
  assert.equal(publicSignals.length, 4);

  console.log("PASS: Verification key exported");

  const valid = await snarkjs.groth16.verify(
    verificationKey,
    publicSignals,
    proof
  );

  assert.equal(valid, true);

  console.log("PASS: Groth16 proof verified");

  const tampered = [...publicSignals];

  tampered[0] = (
    BigInt(tampered[0]) + 1n
  ).toString();

  const invalid = await snarkjs.groth16.verify(
    verificationKey,
    tampered,
    proof
  );

  assert.equal(invalid, false);

  console.log("PASS: Tampered commitment rejected");
  console.log("PASS: V3-R5-C3 actual circuit verification");
}

main().then(
  () => {
    clearTimeout(watchdog);
    process.exit(0);
  },
  error => {
    console.error("FAIL:", error.stack ?? error);
    clearTimeout(watchdog);
    process.exit(1);
  }
);
JS
)
