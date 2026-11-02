import assert from "node:assert/strict";
import {
  createPublicClient,
  custom,
  isAddressEqual,
  recoverTypedDataAddress,
  verifyTypedData,
} from "viem";
import { foundry } from "viem/chains";
import {
  toSimple7702SmartAccount,
} from "viem/account-abstraction";
import {
  createKeycardAccount,
} from "../src/keycard-account.mjs";

const owner = createKeycardAccount({
  binary: process.env.KOHAKU_KEYCARD_CLI,
});

let rpcCalls = 0;
let typedDataCalls = 0;
let signedTypedData;

// Capture the exact EIP-712 payload viem asks Keycard to sign.
const observedOwner = {
  ...owner,
  async signTypedData(typedData) {
    typedDataCalls++;
    signedTypedData = typedData;
    return owner.signTypedData(typedData);
  },
};

const client = createPublicClient({
  chain: foundry,
  transport: custom({
    async request({ method }) {
      rpcCalls++;
      throw new Error(`RPC forbidden: ${method}`);
    },
  }),
});

const smartAccount = await toSimple7702SmartAccount({
  client,
  owner: observedOwner,
});

const address = await smartAccount.getAddress();

assert.ok(isAddressEqual(address, owner.address));

console.log("Keycard owner:", owner.address);
console.log("Simple7702 account:", address);
console.log("Development chain:", foundry.id);

const callData = await smartAccount.encodeCalls([
  {
    to: owner.address,
    value: 0n,
    data: "0x",
  },
]);

// Offline fixture. No bundler or chain connection.
const operation = {
  sender: address,
  nonce: 0n,
  callData,
  callGasLimit: 100_000n,
  verificationGasLimit: 200_000n,
  preVerificationGas: 40_000n,
  maxFeePerGas: 1_000_000_000n,
  maxPriorityFeePerGas: 100_000_000n,
};

console.log("=== Sign UserOperation on hardware ===");

const signature = await smartAccount.signUserOperation({
  ...operation,
  chainId: foundry.id,
});

assert.match(signature, /^0x[0-9a-fA-F]{130}$/);
assert.equal(typedDataCalls, 1);
assert.ok(signedTypedData);

console.log("PASS: Simple7702 delegated to Keycard");

const recovered = await recoverTypedDataAddress({
  ...signedTypedData,
  signature,
});

assert.ok(isAddressEqual(recovered, owner.address));

console.log("Recovered signer:", recovered);
console.log("PASS: Hardware UserOperation signature recovered");

const valid = await verifyTypedData({
  ...signedTypedData,
  address: owner.address,
  signature,
});

assert.equal(valid, true);

console.log("PASS: UserOperation EIP-712 signature verified");

// The signature must not authorize another chain.
const changedChain = await verifyTypedData({
  ...signedTypedData,
  domain: {
    ...signedTypedData.domain,
    chainId: 31338,
  },
  address: owner.address,
  signature,
});

assert.equal(changedChain, false);

console.log("PASS: Modified chain ID rejected");

assert.equal(rpcCalls, 0);

console.log("PASS: Zero RPC calls");
console.log("PASS: No UserOperation broadcast");
console.log("PASS: Real Keycard Simple7702 signing verified");
