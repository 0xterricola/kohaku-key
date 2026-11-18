import { execFileSync } from "node:child_process";
import {
  getAddress,
  hashMessage,
  hashTypedData,
  recoverAddress,
  recoverTransactionAddress,
  parseSignature,
  keccak256,
  serializeTransaction,
  isAddressEqual,
  padHex,
  serializeSignature,
} from "viem";
import { hashAuthorization } from "viem/utils";
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

  async function signDigest(digest) {
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

    const recovered = await recoverAddress({
      hash: digest,
      signature,
    });

    if (!isAddressEqual(recovered, address)) {
      throw new Error(
        "Keycard signature does not match account",
      );
    }

    return signature;
  }

  return toAccount({
    address,

    async signMessage({ message }) {
      return signDigest(hashMessage(message));
    },

    async signTransaction(
      transaction,
      { serializer = serializeTransaction } = {},
    ) {
      if (transaction.type !== "eip1559") {
        throw new Error("Only EIP-1559 transactions are supported");
      }

      if (
        !Number.isSafeInteger(transaction.chainId) ||
        transaction.chainId <= 0 ||
        !Number.isSafeInteger(transaction.nonce) ||
        transaction.nonce < 0
      ) {
        throw new Error("Explicit chain ID and nonce required");
      }

      if (
        typeof transaction.gas !== "bigint" ||
        transaction.gas <= 0n ||
        typeof transaction.value !== "bigint" ||
        transaction.value < 0n ||
        typeof transaction.maxFeePerGas !== "bigint" ||
        typeof transaction.maxPriorityFeePerGas !== "bigint" ||
        transaction.maxPriorityFeePerGas < 0n ||
        transaction.maxFeePerGas < transaction.maxPriorityFeePerGas
      ) {
        throw new Error("Invalid or missing transaction values");
      }

      if (!transaction.to) {
        throw new Error("Explicit recipient required");
      }

      const unsigned = await serializer(transaction);
      const digest = keccak256(unsigned);
      const signature = await signDigest(digest);

      const signed = await serializer(
        transaction,
        parseSignature(signature),
      );

      const recovered = await recoverTransactionAddress({
        serializedTransaction: signed,
      });

      if (!isAddressEqual(recovered, address)) {
        throw new Error("Transaction sender mismatch");
      }

      return signed;
    },

    async signTypedData(typedData) {
      return signDigest(hashTypedData(typedData));
    },

    async signAuthorization(authorization) {
      const {
        chainId,
        nonce,
      } = authorization;

      const contractAddress = getAddress(
        authorization.contractAddress ?? authorization.address,
      );

      if (!Number.isSafeInteger(chainId) || chainId <= 0) {
        throw new Error("Explicit nonzero chain ID required");
      }

      if (!Number.isSafeInteger(nonce) || nonce < 0) {
        throw new Error("Explicit valid nonce required");
      }

      const digest = hashAuthorization({
        contractAddress,
        chainId,
        nonce,
      });

      const signature = await signDigest(digest);

      return {
        address: contractAddress,
        chainId,
        nonce,
        ...parseSignature(signature),
      };
    },
  });
}
