import assert from "node:assert/strict";
import {
  createWalletClient,
  custom,
  isAddressEqual,
  keccak256,
  numberToHex,
  parseTransaction,
  recoverAddress,
  recoverTransactionAddress,
  serializeTransaction,
} from "viem";
import { sepolia } from "viem/chains";
import { createKeycardAccount } from "../src/keycard-account.mjs";

const account = createKeycardAccount({
  binary: process.env.KOHAKU_KEYCARD_CLI,
});

const rpcCalls = [];

const wallet = createWalletClient({
  account,
  chain: sepolia,
  transport: custom({
    async request({ method }) {
      rpcCalls.push(method);

      if (method === "eth_chainId") {
        return numberToHex(sepolia.id);
      }

      throw new Error(`Unexpected RPC request: ${method}`);
    },
  }),
});

// Zero-value self-transfer, Sepolia only.
// This transaction will NEVER be broadcast.
const transaction = {
  type: "eip1559",
  chainId: sepolia.id,
  nonce: 0,
  to: account.address,
  value: 0n,
  gas: 21_000n,
  maxFeePerGas: 3_000_000_000n,
  maxPriorityFeePerGas: 1_000_000_000n,
  data: "0x",
  accessList: [],
};

console.log("Hardware account:", account.address);
console.log("Chain:", sepolia.name);
console.log("Unsigned hash:", keccak256(
  serializeTransaction(transaction),
));

const signed = await wallet.signTransaction(transaction);

assert.ok(signed.startsWith("0x02"));
console.log("PASS: EIP-1559 transaction serialized");

const parsed = parseTransaction(signed);

assert.equal(parsed.type, "eip1559");
assert.equal(parsed.chainId, sepolia.id);
assert.equal(parsed.nonce, transaction.nonce);
assert.ok(isAddressEqual(parsed.to, transaction.to));
assert.equal(parsed.value ?? 0n, transaction.value);

console.log("PASS: Transaction fields preserved");

const recovered = await recoverTransactionAddress({
  serializedTransaction: signed,
});

console.log("Recovered sender:", recovered);

assert.ok(isAddressEqual(recovered, account.address));
console.log("PASS: Hardware transaction signature verified");

const alteredDigest = keccak256(
  serializeTransaction({
    ...transaction,
    nonce: transaction.nonce + 1,
  }),
);

const alteredSender = await recoverAddress({
  hash: alteredDigest,
  signature: {
    r: parsed.r,
    s: parsed.s,
    yParity: parsed.yParity,
  },
});

assert.equal(
  isAddressEqual(alteredSender, account.address),
  false,
);

console.log("PASS: Modified transaction invalidates signature");

assert.ok(rpcCalls.length >= 1);
assert.ok(rpcCalls.every(method => method === "eth_chainId"));

console.log("PASS: Only local chain-ID mock used");
console.log("PASS: No transaction broadcast");
