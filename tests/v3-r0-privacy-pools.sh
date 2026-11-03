#!/usr/bin/env bash
set -euo pipefail

cli="${KOHAKU_CLI_DIR:-$HOME/Developer/kohaku-cli}"

test -f "$cli/node_modules/@kohaku-eth/privacy-pools/dist/index.js"

(
cd "$cli"

node --import tsx --input-type=module <<'JS'
import assert from "node:assert/strict";
import { SignatureSecretManager } from "@kohaku-eth/privacy-pools";
import { privateKeyToAccount } from "viem/accounts";
import {
  concat, hexToBigInt, keccak256, parseSignature,
  slice, stringToHex, toHex
} from "viem";

// Synthetic test keys only. Never use for real funds.
const owner = privateKeyToAccount("0x" + "11".repeat(32));
const alternate = privateKeyToAccount("0x" + "22".repeat(32));

const inputs = {
  chainId: 11155111n,
  entrypointAddress:
    0x34A2068192b1297f2a7f85D7D8CdE66F8F0921cBn,
};

const signer = {
  signEnvelope: (envelope) => owner.signTypedData(envelope),
};

const host = {
  keystore: {
    deriveAt: async () => {
      throw new Error("Software keystore intentionally disabled");
    },
  },
};

function manager(deviceSigner = signer) {
  return SignatureSecretManager({
    host,
    accountIndex: 0,
    signer: deviceSigner,
  });
}

function envelope(depositIndex, secretIndex, context = inputs) {
  return {
    domain: {
      name: "PrivacyPools Keychain",
      version: "1",
      chainId: Number(context.chainId),
      verifyingContract: toHex(context.entrypointAddress, {
        size: 20,
      }),
      salt: keccak256(stringToHex("privacypools")),
    },
    types: {
      PrivacyPoolNote: [
        { name: "depositIndex", type: "uint64" },
        { name: "secretIndex", type: "uint64" },
      ],
    },
    primaryType: "PrivacyPoolNote",
    message: {
      depositIndex: BigInt(depositIndex),
      secretIndex: BigInt(secretIndex),
    },
  };
}

const curveN =
  0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141n;

function referenceField(tag, signature) {
  const { r, s } = parseSignature(signature);
  const sValue = BigInt(s);
  const lowS =
    sValue > curveN / 2n ? curveN - sValue : sValue;

  const canonical = concat([
    toHex(BigInt(r), { size: 32 }),
    toHex(lowS, { size: 32 }),
  ]);

  return hexToBigInt(
    slice(
      keccak256(concat([stringToHex(tag), canonical])),
      0,
      31
    )
  );
}

const first = manager();
const restarted = manager();

const d0 = await first.getDepositSecrets({
  ...inputs, depositIndex: 0
});

const d0Recovered = await restarted.getDepositSecrets({
  ...inputs, depositIndex: 0
});

assert.deepEqual(d0, d0Recovered);
console.log("PASS: Deposit secrets survive manager restart");

const signature = await signer.signEnvelope(envelope(0, 0));

assert.equal(d0.nullifier, referenceField("nullifier", signature));
assert.equal(d0.salt, referenceField("salt", signature));
console.log("PASS: Independent canonical signature derivation");

const initial = await first.getSecrets({
  ...inputs, depositIndex: 0, withdrawIndex: 0
});

assert.deepEqual(initial, d0);
console.log("PASS: Deposit and initial withdrawal secrets agree");

const w1 = await first.getSecrets({
  ...inputs, depositIndex: 0, withdrawIndex: 1
});

const w1Recovered = await restarted.getSecrets({
  ...inputs, depositIndex: 0, withdrawIndex: 1
});

assert.deepEqual(w1, w1Recovered);
assert.notEqual(w1.precommitment, d0.precommitment);
console.log("PASS: Partial-withdrawal secrets reproduce");

const d1 = await first.getDepositSecrets({
  ...inputs, depositIndex: 1
});

assert.notEqual(d0.precommitment, d1.precommitment);
console.log("PASS: Deposit indexes remain distinct");

const changedChain = await first.getDepositSecrets({
  ...inputs, chainId: 1n, depositIndex: 0
});

assert.notEqual(d0.precommitment, changedChain.precommitment);
console.log("PASS: Chain identity binds credential derivation");

const ephemeral = await first.deriveEphemeralSigner({
  ...inputs, depositIndex: 0, withdrawIndex: 1
});

const recoveredEphemeral = await restarted.deriveEphemeralSigner({
  ...inputs, depositIndex: 0, withdrawIndex: 1
});

assert.equal(ephemeral, recoveredEphemeral);
assert.equal(
  ephemeral,
  toHex(referenceField("signer", await signer.signEnvelope(
    envelope(0, 1)
  )), { size: 32 })
);
console.log("PASS: Ephemeral sender derivation reproduces");

let signCount = 0;
const nondeterministicSigner = {
  signEnvelope: (note) =>
    (++signCount % 2 ? owner : alternate).signTypedData(note),
};

await assert.rejects(
  () => manager(nondeterministicSigner).getDepositSecrets({
    ...inputs, depositIndex: 0
  }),
  /not deterministic/
);

console.log("PASS: Nondeterministic signer rejected");
console.log("PASS: Offline V3-R0 reference tests complete");
JS
)
