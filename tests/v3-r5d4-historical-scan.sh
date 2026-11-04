#!/usr/bin/env bash
set -euo pipefail

cli="${KOHAKU_CLI_DIR:-$HOME/Developer/kohaku-cli}"

(
cd "$cli"

node --input-type=module <<'JS'
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import {
  mkdir, readdir, readFile, writeFile,
  rename, open, unlink
} from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";
import { createPublicClient, http } from "viem";
import { sepolia } from "viem/chains";

const deployment = 8587019n;
const chainId = 11155111;

const pool =
  "0x644d5A2554d36e27509254F32ccfeBe8cd58861f";

const entrypoint =
  "0x34A2068192b1297f2a7f85D7D8CdE66F8F0921cB";

const addresses = [pool, entrypoint];
const knownBlock = 11180244n;

const knownTx =
  "0x8a9a5ae9a55a94ba86888a5c594b348f29e476b84e4f2c5948e401cbe3475a75";

const chunkSize = Number(process.env.R5D4_CHUNK_SIZE ?? 5001);
const maxChunks = Number(process.env.R5D4_MAX_CHUNKS ?? 3);

assert.ok(Number.isSafeInteger(chunkSize));
assert.ok(chunkSize >= 1 && chunkSize <= 10001);
assert.ok(Number.isSafeInteger(maxChunks));
assert.ok(maxChunks >= 1 && maxChunks <= 100);

const directory = join(
  homedir(),
  "Library",
  "Application Support",
  "KohakuKeyResearch",
  "v3-r5d4-sepolia-v1"
);

const client = createPublicClient({
  chain: sepolia,
  transport: http(
    process.env.SEPOLIA_RPC_URL ??
      "https://sepolia.gateway.tenderly.co",
    { timeout: 25000, retryCount: 0 }
  )
});

const sleep = ms =>
  new Promise(resolve => setTimeout(resolve, ms));

const pad = n => n.toString().padStart(12, "0");

const hashLogs = logs =>
  createHash("sha256")
    .update(JSON.stringify(logs))
    .digest("hex");

let lastRequest = 0;

async function rpc(label, operation) {
  for (let attempt = 0; attempt < 3; attempt++) {
    const delay = Math.max(
      0, lastRequest + 3000 - Date.now()
    );

    if (delay) await sleep(delay);

    lastRequest = Date.now();
    console.log(`RPC: ${label}`);

    try {
      return await operation();
    } catch (error) {
      const reason = [
        error.name,
        error.shortMessage,
        error.details,
        error.cause?.details
      ].filter(Boolean).join(" ");

      const limited =
        /rate.limit|LimitExceeded|429/i.test(reason);

      if (!limited || attempt === 2) {
        throw new Error(
          `${label}: ${error.name}; checkpoint not advanced`
        );
      }

      const backoff = 8000 * (2 ** attempt);

      console.log(
        `THROTTLED: retry ${attempt + 1}/2`
      );

      await sleep(backoff);
    }
  }
}

function normalize(log, from, to) {
  assert.ok(log.blockNumber >= from);
  assert.ok(log.blockNumber <= to);
  assert.ok(log.blockHash);
  assert.ok(log.transactionHash);
  assert.ok(log.transactionIndex != null);
  assert.ok(log.logIndex != null);
  assert.ok(log.removed !== true);

  const address = log.address.toLowerCase();

  assert.ok(addresses.some(
    a => a.toLowerCase() === address
  ));

  return {
    address,
    blockNumber: log.blockNumber.toString(),
    blockHash: log.blockHash,
    transactionHash: log.transactionHash,
    transactionIndex: Number(log.transactionIndex),
    logIndex: Number(log.logIndex),
    topics: log.topics,
    data: log.data
  };
}

function validateLogs(logs, from, to) {
  const ids = new Set();
  let previous = null;

  for (const log of logs) {
    const block = BigInt(log.blockNumber);

    assert.ok(block >= from && block <= to);

    const id = [
      log.blockHash,
      log.transactionHash,
      log.logIndex
    ].join(":");

    assert.ok(!ids.has(id), "Duplicate log");
    ids.add(id);

    const position = [
      block,
      log.transactionIndex,
      log.logIndex
    ];

    if (previous) {
      const ordered =
        position[0] > previous[0] ||
        (position[0] === previous[0] &&
          (position[1] > previous[1] ||
            (position[1] === previous[1] &&
              position[2] > previous[2])));

      assert.ok(ordered, "Logs out of order");
    }

    previous = position;
  }
}

async function loadCheckpoints() {
  const files = (await readdir(directory))
    .filter(name =>
      /^chunk-\d{12}-\d{12}\.json$/.test(name)
    )
    .sort();

  let next = deployment;
  let last = null;
  let totalLogs = 0;

  for (const name of files) {
    const checkpoint = JSON.parse(
      await readFile(join(directory, name), "utf8")
    );

    const from = BigInt(checkpoint.fromBlock);
    const to = BigInt(checkpoint.toBlock);

    assert.equal(checkpoint.version, 1);
    assert.equal(checkpoint.chainId, chainId);
    assert.equal(
      checkpoint.pool.toLowerCase(),
      pool.toLowerCase()
    );
    assert.equal(
      checkpoint.entrypoint.toLowerCase(),
      entrypoint.toLowerCase()
    );

    assert.equal(from, next);
    assert.ok(to >= from);

    assert.equal(
      name,
      `chunk-${pad(from)}-${pad(to)}.json`
    );

    assert.equal(
      checkpoint.logSha256,
      hashLogs(checkpoint.logs)
    );

    validateLogs(checkpoint.logs, from, to);

    totalLogs += checkpoint.logs.length;
    next = to + 1n;
    last = checkpoint;
  }

  return { next, last, count: files.length, totalLogs };
}

async function main() {
  await mkdir(directory, {
    recursive: true,
    mode: 0o700
  });

  // Prevent two scanner processes from advancing
  // the same checkpoint sequence concurrently.
  const lockPath = join(directory, ".scan.lock");
  const lock = await open(lockPath, "wx", 0o600);

  try {
    console.log("=== R5-D4B historical scanner ===");

    assert.equal(
      await rpc("chain ID", () => client.getChainId()),
      chainId
    );

    const finalized = await rpc(
      "finalized block",
      () => client.getBlock({ blockTag: "finalized" })
    );

    assert.ok(finalized.number >= deployment);
    assert.ok(finalized.hash);

    console.log(
      "Finalized target:",
      finalized.number.toString()
    );

    const saved = await loadCheckpoints();

    console.log(
      `Saved chunks: ${saved.count}; logs: ${saved.totalLogs}`
    );

    let next = saved.next;

    if (saved.last) {
      const previousEnd =
        BigInt(saved.last.toBlock);

      const anchor = await rpc(
        "verify saved chain anchor",
        () => client.getBlock({
          blockNumber: previousEnd
        })
      );

      assert.equal(
        anchor.hash,
        saved.last.endBlockHash,
        "Stored chain anchor changed"
      );

      assert.ok(previousEnd <= finalized.number);

      console.log("PASS: Saved chain anchor verified");
      console.log("PASS: Scan resumes without gaps");
    }

    for (
      let i = 0;
      i < maxChunks && next <= finalized.number;
      i++
    ) {
      const from = next;

      const to = from + BigInt(chunkSize) - 1n <
        finalized.number
          ? from + BigInt(chunkSize) - 1n
          : finalized.number;

      console.log(
        `\nSCAN ${i + 1}/${maxChunks}: ${from}-${to}`
      );

      const raw = await rpc(
        "historical logs",
        () => client.getLogs({
          address: addresses,
          fromBlock: from,
          toBlock: to
        })
      );

      const logs = raw.map(
        log => normalize(log, from, to)
      );

      validateLogs(logs, from, to);

      if (from <= knownBlock && knownBlock <= to) {
        assert.equal(
          logs.filter(
            log => log.transactionHash === knownTx
          ).length,
          3,
          "Known deposit positive control missing"
        );

        console.log(
          "PASS: Known deposit positive control"
        );
      }

      const anchor = await rpc(
        "verify chunk end block",
        () => client.getBlock({
          blockNumber: to
        })
      );

      assert.equal(anchor.number, to);
      assert.ok(anchor.hash);

      const checkpoint = {
        version: 1,
        chainId,
        pool,
        entrypoint,
        fromBlock: from.toString(),
        toBlock: to.toString(),
        endBlockHash: anchor.hash,
        logSha256: hashLogs(logs),
        logs
      };

      const filename =
        `chunk-${pad(from)}-${pad(to)}.json`;

      const destination =
        join(directory, filename);

      const pending =
        `${destination}.pending-${process.pid}`;

      await writeFile(
        pending,
        JSON.stringify(checkpoint) + "\n",
        { flag: "wx", mode: 0o600 }
      );

      await rename(pending, destination);

      next = to + 1n;

      console.log(
        `PASS: ${from}-${to}: ${logs.length} logs`
      );
      console.log("PASS: Atomic checkpoint saved");
    }

    console.log("\n=== R5-D4B result ===");
    console.log(
      "Next unscanned block:",
      next.toString()
    );
    console.log(
      "Finalized target:",
      finalized.number.toString()
    );

    if (next > finalized.number) {
      console.log(
        "PASS: Full finalized-range query coverage"
      );
    } else {
      console.log(
        "CHECKPOINT: Partial coverage, resumable"
      );
    }

    console.log("PASS: R5-D4B scanner execution");
    console.log(
      "No credentials, signing, or transactions"
    );
  } finally {
    await lock.close();
    await unlink(lockPath);
  }
}

main().then(
  () => process.exit(0),
  error => {
    console.error(
      "BLOCKED:",
      error.message
    );
    process.exit(1);
  }
);
JS
)
