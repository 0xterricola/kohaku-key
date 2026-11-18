const DECIMAL = /^(0|[1-9][0-9]*)$/;
const ADDRESS = /^0x[0-9a-f]{40}$/;

function unsigned(value, name, safeNumber = false) {
  if (!DECIMAL.test(value)) {
    throw new Error(`Invalid ${name}`);
  }

  const number = BigInt(value);

  if (safeNumber && number > BigInt(Number.MAX_SAFE_INTEGER)) {
    throw new Error(`${name} exceeds safe SDK index range`);
  }

  return safeNumber ? Number(number) : number;
}

function encode(id) {
  return [
    "kkid",
    "v1",
    "privacy-pools-v1",
    "eip155",
    id.chainId.toString(),
    `0x${id.entrypointAddress.toString(16).padStart(40, "0")}`,
    String(id.accountIndex),
    String(id.depositIndex),
    id.role,
    String(id.secretIndex),
  ].join(":");
}

export function parseCredentialId(text) {
  if (typeof text !== "string") {
    throw new Error("Credential ID must be a string");
  }

  const parts = text.split(":");

  if (
    parts.length !== 10 ||
    parts[0] !== "kkid" ||
    parts[1] !== "v1" ||
    parts[2] !== "privacy-pools-v1" ||
    parts[3] !== "eip155" ||
    !ADDRESS.test(parts[5])
  ) {
    throw new Error("Invalid credential identifier format");
  }

  const id = {
    chainId: unsigned(parts[4], "chainId"),
    entrypointAddress: BigInt(parts[5]),
    accountIndex: unsigned(parts[6], "accountIndex", true),
    depositIndex: unsigned(parts[7], "depositIndex", true),
    role: parts[8],
    secretIndex: unsigned(parts[9], "secretIndex", true),
  };

  if (
    !(
      (id.role === "deposit" && id.secretIndex === 0) ||
      (id.role === "withdraw" && id.secretIndex >= 1)
    )
  ) {
    throw new Error("Invalid credential role or secret index");
  }

  if (encode(id) !== text) {
    throw new Error("Noncanonical credential identifier");
  }

  return Object.freeze(id);
}

export function formatCredentialId(id) {
  const canonical = encode(id);
  parseCredentialId(canonical);
  return canonical;
}

export function sdkCoordinates(text, expected) {
  const id = parseCredentialId(text);

  if (
    id.chainId !== BigInt(expected.chainId) ||
    id.entrypointAddress !== BigInt(expected.entrypointAddress) ||
    id.accountIndex !== (expected.accountIndex ?? 0)
  ) {
    throw new Error("Credential context mismatch");
  }

  const coordinates = {
    chainId: id.chainId,
    entrypointAddress: id.entrypointAddress,
    depositIndex: id.depositIndex,
  };

  return id.role === "withdraw"
    ? { ...coordinates, withdrawIndex: id.secretIndex }
    : coordinates;
}
