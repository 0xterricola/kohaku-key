import assert from "node:assert/strict";
import { createWalletClient, custom } from "viem";
import { recoverMessageAddress, isAddressEqual } from "viem";
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

console.log("Hardware account:", account.address);
console.log("Account source:", account.source);

assert.equal(account.type, "local");

const messages = [
  "Kohaku Key V1 - viem custom account",
  { raw: "0x4b6f68616b75204b6579" },
];

for (const message of messages) {
  const signature = await wallet.signMessage({ message });

  const recovered = await recoverMessageAddress({
    message,
    signature,
  });

  assert.ok(
    isAddressEqual(recovered, account.address),
    "Hardware signature address mismatch",
  );

  console.log(
    "PASS:",
    typeof message === "string"
      ? "UTF-8 EIP-191 signing"
      : "Raw-byte EIP-191 signing",
  );
}

console.log("PASS: Viem delegated signing to Keycard");
console.log("PASS: No network transactions");
