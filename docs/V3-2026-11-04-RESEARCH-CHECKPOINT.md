# Kohaku Key V3 — Research Checkpoint

**Date:** November 4, 2026
**Status:** Physical hardware-backed Privacy Pools prototype verified offline. Real Sepolia deposit pending.
**CLI branch:** `research/v3-r5e5b9k-deposit-integration`
**Verified CLI commit:** `7ffd14c`

## Architecture

Kohaku Key V3 integrates a physical Keycard 4.0 with the Privacy Pools V1 SDK and Kohaku CLI.

The card derives deterministic BIP-85 entropy and performs ECDSA signatures. The existing Go-to-Node anonymous-pipe adapter transports the BIP-85 root into macOS process memory for the SDK-compatible credential derivation.

This is a research prototype, not a production-ready hardware wallet.

## Frozen V3-R3 derivation contract

- EVM signer path: `m/44'/60'/0'/0/0`
- BIP-85 path: `m/83696968'/128169'/32'/0'`
- BIP-85 root: 32 bytes
- Domain: `kohaku-key/v3-r3/privacy-pools-v1/deriveAt`
- SDK manager: legacy Privacy Pools `SecretManager`
- Account index: 0
- Tested deposit index: 17

Derivation:

```text
HMAC-SHA256(
  key = BIP85_root,
  message = UTF8(domain) || 0x00 || UTF8(keyPath)
)
```

This is not BIP-32. Switching to the SDK `SignatureSecretManager` or changing R3 paths would break credential compatibility.

Credential identifiers follow:

```text
kkid:v1:privacy-pools-v1:eip155:<chainId>:<entrypoint>:<accountIndex>:<depositIndex>:<role>:<secretIndex>
```

## Verified milestones

| Checkpoint | Result |
|---|---|
| V3-R3 | Physical BIP-85 Privacy Pools credential derivation |
| V3-R5-E | Deterministic credential identifier and recovery research |
| K9 | Physical offline credential and EIP-1559 signing proof |
| K10–K11R | Permanent regression and TypeScript validation |
| K14 | Reusable R3 credential provider |
| K15 | Offline SDK deposit planner |
| K16 | Two-session physical Keycard credential IPC |
| K17 | Approved physical ECDSA signing and independent viem verification |
| K18 | Real Sepolia hardware-derived deposit calldata |
| K19 | Read-only deployment, funding, nonce and gas feasibility |
| K20 | SDK deposit event schema and snapshot inspection |
| K21R6 | Complete registered-pool-scoped post-snapshot scan |
| K21R7 | Hardware index-17 credential compared locally against cached history |

### K21R7 evidence

CLI commit: `7ffd14c`.

- 16 focused regression tests passed.
- Two authenticated Keycard sessions reproduced the same credential root.
- Precommitment, nullifier and salt reconstructed consistently.
- No match for index-17 precommitment in cached public history.
- Credential comparison was entirely local, without RPC requests.
- No real transaction was signed or broadcast.

## Sepolia evidence

- Chain ID: `11155111`
- Entrypoint: `0x34A2068192b1297f2a7f85D7D8CdE66F8F0921cB`
- Snapshot head: `11,954,218`
- Snapshot deposits: `1,153`
- Post-snapshot deposits: `3`
- Authorized pools: `3`
- Cached history checked through block: `12,067,822`
- Index-17 precommitment reuse detected: no

K19 observed a sender balance of 0.05 Sepolia ETH, pending nonce 0, and successful synthetic deposit simulation for a planned 0.002 ETH deposit. These observations require refreshing before live execution.

## Remaining V3 work

1. Independently audit the older bundled snapshot using historical on-chain logs (K22).
2. Refresh public deposit history and recheck index-17 credential reuse.
3. Verify live contract state, actual transaction parameters, balance, gas and simulation.
4. Require explicit approval before physical signing and broadcasting.
5. Verify transaction receipt, deposit registration and independent hardware-backed note recovery.

K22 was in progress when this documentation checkpoint was created. Its result is not asserted here.

## Security limitations

The current V3 architecture exports BIP-85 entropy into macOS process memory. Anonymous IPC and buffer clearing do not guarantee complete secret erasure or hardware isolation.

Full withdrawal execution, note recovery across restarts, and comprehensive protocol security validation remain outside the completed deposit-signing proof.

## Repository responsibilities

- `kohaku-key`: architecture, security research, experiments and evidence.
- `kohaku-cli`: CLI integration, executable checkpoints and regression tests.
- `kohaku-sdk-research`: Privacy Pools SDK research and deposit-index support.

See [Keycard Shell architecture draft](V4-KEYCARD-SHELL-ARCHITECTURE-DRAFT.md).
