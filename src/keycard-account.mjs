import { execFileSync } from "node:child_process";
import {
  getAddress,
  hashMessage,
  isAddressEqual,
  padHex,
  recoverMessageAddress,
  serializeSignature,
} from "viem";
import { publicKeyToAddress, toAccount } from "viem/accounts";

export function createKeycardAccount({
  binary,
  path = "m/44'/60'/0'/0/0",
}) {
  if (!binary) {
    throw new Error("Keycard CLI binary is required");
  }

  if (!process.env.KEYCARD_PIN) {
    throw new Error("KEYCARD_PIN is required");
  }

  function command(name, args = []) {
    const output = execFileSync(
      binary,
      [name, ...args, "--json", "--log-level", "error"],
      {
        encoding: "utf8",
        maxBuffer: 1024 * 1024,
        stdio: ["ignore", "pipe", "pipe"],
      },
    );

    return JSON.parse(output);
  }

  const exported = command("export-public-key", [
    "--path", path,
  ]);

  const address = getAddress(exported.address);
  const publicKeyAddress = publicKeyToAddress(
    exported.public_key,
  );

  if (!isAddressEqual(address, publicKeyAddress)) {
    throw new Error("Keycard public key/address mismatch");
  }

  return toAccount({
    address,

    async signMessage({ message }) {
      const digest = hashMessage(message);

      const result = command("sign", [
        "--hex", digest,
        "--path", path,
        "--algo", "ecdsa",
      ]);

      const parity = Number(result.signature_v);

      if (parity !== 0 && parity !== 1) {
        throw new Error("Invalid Keycard recovery parity");
      }

      const signature = serializeSignature({
        r: padHex(result.signature_r, { size: 32 }),
        s: padHex(result.signature_s, { size: 32 }),
        yParity: parity,
      });

      const recovered = await recoverMessageAddress({
        message,
        signature,
      });

      if (!isAddressEqual(recovered, address)) {
        throw new Error(
          "Keycard signature does not match account",
        );
      }

      return signature;
    },

    async signTransaction() {
      throw new Error(
        "Keycard transaction signing not implemented",
      );
    },

    async signTypedData() {
      throw new Error(
        "Keycard EIP-712 signing not implemented",
      );
    },
  });
}
