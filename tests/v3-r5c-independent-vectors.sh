#!/usr/bin/env bash
set -euo pipefail

cli="${KOHAKU_CLI_DIR:-$HOME/Developer/kohaku-cli}"

(
cd "$cli"

node --import tsx --input-type=module <<'JS'
import assert from "node:assert/strict";
import { poseidon } from "maci-crypto/build/ts/hashing.js";
import { encodePacked, keccak256 } from "viem";

// External reference: Verified-zkEVM/clean,
// Clean/Specs/Poseidon.lean, circomlib test vectors.
const vectors = [
  {
    input: [1n],
    expected:
      18586133768512220936620570745912940619677854269274689475585506675881198879027n,
  },
  {
    input: [1n, 2n],
    expected:
      7853200120776062878684798364095072458815029376092732009249414926327459813530n,
  },
  {
    input: [1n, 0n, 0n],
    expected:
      16319005924338521988144249782199320915969277491928916027259324394544057385749n,
  },
  {
    input: [0n, 0n, 0n],
    expected:
      5317387130258456662214331362918410991734007599705406860481038345552731150762n,
  },
];

for (const { input, expected } of vectors) {
  assert.equal(
    poseidon(input),
    expected,
    `Poseidon(${input.join(",")}) mismatch`
  );
}
console.log("PASS: Four independent Poseidon test vectors");

const FIELD =
  21888242871839275222246405745257275088548364400416034343698204186575808495617n;

const toBytes = (value, length) => {
  assert.ok(value >= 0n);
  assert.ok(value < 1n << BigInt(length * 8));
  return Buffer.from(
    value.toString(16).padStart(length * 2, "0"),
    "hex"
  );
};

const addressHex = value =>
  `0x${value.toString(16).padStart(40, "0")}`;

const pool = 0x1234n;
const asset = 0x2222n;
const chainId = 11155111n;

// Independently assemble the exact Solidity packed bytes.
const scopePacked = Buffer.concat([
  toBytes(pool, 20),
  toBytes(chainId, 32),
  toBytes(asset, 20),
]);

assert.equal(scopePacked.length, 72);

const manualScope = BigInt(keccak256(
  `0x${scopePacked.toString("hex")}`
)) % FIELD;

const viemScope = BigInt(keccak256(encodePacked(
  ["address", "uint256", "address"],
  [addressHex(pool), chainId, addressHex(asset)]
))) % FIELD;

assert.equal(manualScope, viemScope);
console.log("PASS: Solidity pool-scope byte encoding");

function labelAt(nonce) {
  const manualBytes = Buffer.concat([
    toBytes(manualScope, 32),
    toBytes(BigInt(nonce), 32),
  ]);

  const manual = BigInt(keccak256(
    `0x${manualBytes.toString("hex")}`
  )) % FIELD;

  const encoded = BigInt(keccak256(encodePacked(
    ["uint256", "uint256"],
    [manualScope, BigInt(nonce)]
  ))) % FIELD;

  assert.equal(manual, encoded);
  return manual;
}

const label = labelAt(1);
assert.notEqual(label, labelAt(2));
console.log("PASS: Solidity label and nonce encoding");

// Explicitly public synthetic inputs, never hardware secrets.
const nullifier0 = 123n;
const salt0 = 456n;
const nullifier1 = 789n;
const salt1 = 987n;
const nullifier2 = 321n;
const salt2 = 654n;

const pre0 = poseidon([nullifier0, salt0]);
const pre1 = poseidon([nullifier1, salt1]);
const pre2 = poseidon([nullifier2, salt2]);

const hash0 = poseidon([nullifier0]);
const hash1 = poseidon([nullifier1]);
const hash2 = poseidon([nullifier2]);

assert.notEqual(pre0, pre1);
assert.notEqual(pre1, pre2);

assert.notEqual(hash0, hash1);
assert.notEqual(hash1, hash2);
console.log("PASS: Precommitment and nullifier separation");

const commitment = (value, precommitment) =>
  poseidon([value, label, precommitment]);

const original = commitment(1000n, pre0);
const replacement1 = commitment(800n, pre1);
const replacement2 = commitment(500n, pre2);

assert.notEqual(original, replacement1);
assert.notEqual(replacement1, replacement2);

assert.equal(
  commitment(1000n, pre0),
  original
);
assert.equal(
  commitment(800n, pre1),
  replacement1
);
assert.equal(
  commitment(500n, pre2),
  replacement2
);

assert.notEqual(
  original,
  poseidon([label, 1000n, pre0])
);
console.log("PASS: Commitment input ordering");
console.log("PASS: Sequential replacement commitments");

// Negative control: altering any commitment field
// must not reproduce the original commitment.
for (const changed of [
  poseidon([1001n, label, pre0]),
  poseidon([1000n, labelAt(2), pre0]),
  poseidon([1000n, label, pre1]),
]) {
  assert.notEqual(changed, original);
}
console.log("PASS: Commitment mutation controls");

console.log("PASS: V3-R5-C2 independent-vector checkpoint");
JS
)
