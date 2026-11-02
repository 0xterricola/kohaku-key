# Kohaku Key — V2 Baseline

**Status:** Iteration 0 — Not yet verified
**Created:** November 2, 2026

## Purpose

Record reproducible hardware, software, upstream,
and network conditions before V2 implementation.

## V1 Reference

Research repository:
https://github.com/0xterricola/kohaku-key

V1 documentation checkpoint: `4978e3c`

Kohaku CLI V1 implementation branch:
`feat/keycard-7702-userop`

V1 implementation checkpoint: `4c7aa87`

Previously verified:

- 538/538 Kohaku CLI tests passed.
- TypeScript typecheck passed.
- Production build passed.
- Offline EIP-1559 hardware signing passed.
- Offline two-call Simple7702 signing passed.
- Zero RPC requests in offline hardware tests.

These results are historical V1 checkpoints.
V2 baseline verification is still pending.

## Hardware Inventory

Previously tested:

- Retail Keycard applet 3.1.
- HID Global OMNIKEY 3x21 reader.
- Ethereum derivation path: m/44'/60'/0'/0/0.

Record during Iteration 0:

- Card firmware/applet version:
- Reader model and firmware:
- Transport:
- Keycard CLI version:
- Keycard Go SDK revision:
- Host operating system:
- Node.js version:
- Go version:
- viem version:
- Kohaku CLI revision:

Do not record PINs or wallet recovery secrets.

## Upstream Dependencies

| Contribution | Verification |
|---|---|
| Kohaku CLI #67 | Pending baseline check |
| Kohaku CLI #68 | Pending baseline check |
| Kohaku CLI #69 | Pending baseline check |
| Keycard Go #20 | Pending branch/release verification |

Do not infer inclusion in an official SDK release
from the existence of a fix commit alone.

## Baseline Tests

From the Kohaku CLI implementation repository:

    npm test
    npm run typecheck
    npm run build

Record:

- Test count:
- Passed:
- Failed:
- Build result:
- Commit:
- Date:

Physical Keycard checks:

- EIP-191:
- EIP-712:
- EIP-1559:
- EIP-7702 authorization:
- Simple7702 UserOperation:
- Recovered address:
- Hardware disconnect behavior:

## Sepolia Prerequisites

Verify:

- Correct Sepolia chain ID: 11155111.
- A supported Ethereum RPC endpoint.
- A compatible ERC-4337 bundler.
- Trusted Simple7702 implementation and code.
- A disposable hardware-backed test account.
- Minimal test ETH funding.
- No mainnet signing or submission.

Record exact provider and implementation selections
when these are verified.

## Iteration 0 Acceptance

- [ ] Upstream status verified.
- [ ] SDK and CLI versions recorded.
- [ ] Existing tests pass.
- [ ] Production build passes.
- [ ] Physical signer baseline passes.
- [ ] Threat model reviewed.
- [ ] Sepolia dependencies identified.
- [ ] V2 implementation branch created.

## Findings

Not started.

## Decision

Iteration 0 gate: OPEN.
