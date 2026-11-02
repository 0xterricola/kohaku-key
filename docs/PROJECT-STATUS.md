# Kohaku Key — Project Status

Updated: November 2, 2026

## Overview

Kohaku Key is a hardware-signer integration project for
Kohaku CLI, using Keycard hardware and viem custom accounts.

The objective is to perform Ethereum signing without
exporting private keys or requiring Kohaku's software
mnemonic for hardware-backed transaction execution.

## Upstream contributions

### Keycard Go #20 — Merged

https://github.com/keycard-tech/keycard-go/pull/20

Fixed legacy ECDSA signature buffer aliasing in
`types/signature.go` within `calculateV()`.

Original:

    rs := append(r, s...)

Fixed:

    rs := append(append([]byte{}, r...), s...)

A regression test reproduced corruption of the original
S component. The test failed before the fix and passed
afterward. The full Go test suite passed.

The fix was independently verified using physical Keycard
hardware: ECDSA verification and Ethereum address recovery
both succeeded.

Merged into upstream `develop` as commit c4cf5cc.
An official SDK/CLI release containing the fix has not
been established by this research.

### Kohaku CLI #67 — External viem signers

https://github.com/kassandraoftroy/kohaku-cli/pull/67

Introduces signer injection into Ethereum and EIP-7702
execution utilities while retaining the software-key path.

The refactor does not by itself enable hardware selection
in CLI commands.

### Kohaku CLI #68 — Keycard integration

https://github.com/kassandraoftroy/kohaku-cli/pull/68

Stacked on #67.

Adds a TypeScript Keycard-backed viem account, physical
hardware integration tests, and an offline Keycard mode
in `transact-raw`.

Current CLI hardware mode:

- `--signer keycard`
- EIP-1559 signing only
- Explicit chain ID, nonce, gas, and fee parameters
- Chain ID 31337 only
- One transaction per invocation
- No mnemonic unlock or private-key derivation
- No RPC or broadcast in the offline signing path

## Tested hardware and software

- Retail Keycard, applet 3.1
- HID Global OMNIKEY 3x21 reader
- Keycard CLI 4.0.0, locally built with corrected SDK
- viem 2.55.19
- Node.js 22.23.4
- Ethereum derivation path: m/44'/60'/0'/0/0

Keycard Shell and newer applet versions have not been
validated in these experiments.

## Verified signing capabilities

| Capability | Result |
| --- | --- |
| Public-key and address discovery | PASS |
| EIP-191 UTF-8 message | PASS |
| EIP-191 raw-byte message | PASS |
| EIP-712 typed data | PASS |
| EIP-1559 serialized transaction | PASS |
| EIP-7702 authorization | PASS |
| Simple7702 ERC-4337 UserOperation | PASS (offline) |
| Kohaku CLI offline transaction command | PASS |
| Live transaction broadcast | NOT TESTED |
| Live bundler execution | NOT TESTED |

The Simple7702 UserOperation test exercised viem's
hardware-backed signing delegation offline. It is not yet
integrated into Kohaku CLI's live UserOperation submission.

## Validation

Kohaku CLI:

- 525 existing regression tests passing
- 4 new CLI safety regression tests passing
- TypeScript typecheck passing
- Production build passing
- Physical Keycard integration passing

CLI safety tests reject broadcasting, incompatible
software-wallet options, missing chain ID, and unknown
signer backends.

No network transaction was submitted.

## Repository structure

- `src/keycard-account.mjs`: research viem account adapter
- `scripts/verify-keycard-account.mjs`: EIP-191 tests
- `scripts/verify-keycard-typed-data.mjs`: EIP-712 tests
- `scripts/verify-keycard-transaction.mjs`: EIP-1559 tests
- `scripts/verify-keycard-authorization.mjs`: EIP-7702 tests
- `scripts/verify-keycard-user-operation.mjs`: Simple7702 tests
- `docs/EXPERIMENT-002.md`: SDK defect investigation
- `docs/V1-PROPOSAL.md`: original implementation proposal

The Kohaku CLI TypeScript implementation lives in
the separate `0xterricola/kohaku-cli` fork.

## Next milestones

1. Address upstream review feedback on #67 and #68.
2. Integrate Keycard into Kohaku CLI's UserOperation path.
3. Replace prototype PIN handling with a safer workflow.
4. Define transaction approval and device lifecycle policies.
5. Validate Keycard Shell separately.
6. Expand chain support and test broadcasting on a testnet.
7. Adopt an official Keycard SDK/CLI release with #20.
