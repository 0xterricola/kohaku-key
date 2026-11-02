import assert from "node:assert/strict";
import {
  createWalletClient,
  custom,
  isAddressEqual,
} from "viem";
import {
  hashAuthorization,
  recoverAuthorizationAddress,
  verifyAuthorization,
} from "viem/utils";
import { createKeycardAccount } from "../src/keycard-account.mjs";

const account = createKeycardAccount({
  binary: process.env.KOHAKU_KEYCARD_CLI,
});

let rpcCalls = 0;

const wallet = createWalletClient({
  account,
  transport: custom({
    async request({ method }) {
      rpcCalls++;
      throw new Error(`Unexpected RPC request: ${method}`);
    },
  }),
});

// Local development chain only.
// Large nonce prevents accidental use at normal account state.
const authorization = {
  contractAddress: "0x1111111111111111111111111111111111111111",
  chainId: 31337,
  nonce: 4294967295,
};

console.log("Hardware account:", account.address);
console.log("Development chain:", authorization.chainId);
console.log(
  "Authorization digest:",
  hashAuthorization(authorization),
);

const signed = await wallet.signAuthorization(authorization);

assert.equal(signed.chainId, authorization.chainId);
assert.equal(signed.nonce, authorization.nonce);
assert.ok(
  isAddressEqual(
    signed.address,
    authorization.contractAddress,
  ),
);

console.log("PASS: EIP-7702 authorization fields preserved");

const recovered = await recoverAuthorizationAddress({
  authorization: signed,
});

assert.ok(isAddressEqual(recovered, account.address));

console.log("Recovered signer:", recovered);
console.log("PASS: Hardware authorization signer recovered");

const valid = await verifyAuthorization({
  address: account.address,
  authorization: signed,
});

assert.equal(valid, true);
console.log("PASS: EIP-7702 authorization verified");

const alteredNonce = await verifyAuthorization({
  address: account.address,
  authorization: {
    ...signed,
    nonce: signed.nonce + 1,
  },
});

assert.equal(alteredNonce, false);
console.log("PASS: Modified nonce rejected");

const alteredDelegate = await verifyAuthorization({
  address: account.address,
  authorization: {
    ...signed,
    address: "0x2222222222222222222222222222222222222222",
  },
});

assert.equal(alteredDelegate, false);
console.log("PASS: Modified delegate rejected");

await assert.rejects(
  () => account.signAuthorization({
    ...authorization,
    chainId: 0,
  }),
  /nonzero chain ID/,
);

console.log("PASS: Cross-chain authorization rejected");

assert.equal(rpcCalls, 0);

console.log("PASS: Zero RPC calls");
console.log("PASS: No authorization broadcast");
console.log("PASS: Viem delegated EIP-7702 signing to Keycard");
