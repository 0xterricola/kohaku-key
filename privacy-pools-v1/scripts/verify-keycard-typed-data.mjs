import assert from "node:assert/strict";
import {
  createWalletClient,
  custom,
  hashTypedData,
  recoverAddress,
  isAddressEqual,
  verifyTypedData,
} from "viem";
import { createKeycardAccount } from "../src/keycard-account.mjs";

const account = createKeycardAccount({
  binary: process.env.KOHAKU_KEYCARD_CLI,
});

const wallet = createWalletClient({
  account,
  transport: custom({
    async request() {
      throw new Error("Network access prohibited");
    },
  }),
});

const typedData = {
  domain: {
    name: "Kohaku Key",
    version: "1",
    chainId: 11155111,
  },
  types: {
    Intent: [
      { name: "action", type: "string" },
      { name: "owner", type: "address" },
      { name: "nonce", type: "uint256" },
    ],
  },
  primaryType: "Intent",
  message: {
    action: "Kohaku Key hardware signing verification",
    owner: account.address,
    nonce: 1n,
  },
};

console.log("Hardware account:", account.address);
console.log("EIP-712 digest:", hashTypedData(typedData));

const signature = await wallet.signTypedData(typedData);

const recovered = await recoverAddress({
  hash: hashTypedData(typedData),
  signature,
});

assert.ok(isAddressEqual(recovered, account.address));

const valid = await verifyTypedData({
  ...typedData,
  address: account.address,
  signature,
});

assert.equal(valid, true);
console.log("PASS: EIP-712 hardware signature verified");

const altered = await verifyTypedData({
  ...typedData,
  message: {
    ...typedData.message,
    nonce: 2n,
  },
  address: account.address,
  signature,
});

assert.equal(altered, false);
console.log("PASS: Modified typed data rejected");

console.log("PASS: Viem delegated EIP-712 signing to Keycard");
console.log("PASS: No network transactions");
