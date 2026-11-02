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
- Keycard Go SDK revision: f64e791 (local patched checkout)
- Host operating system: macOS 27.2 (arm64)
- Node.js version: v22.23.4
- Go version: go1.24.3 darwin/arm64
- viem version: 2.55.19
- Kohaku CLI revision: 4c7aa87

Do not record PINs or wallet recovery secrets.

## Upstream Dependencies

| Contribution | Verification |
|---|---|
| Kohaku CLI #67 | Open — November 2, 2026 |
| Kohaku CLI #68 | Open — November 2, 2026 |
| Kohaku CLI #69 | Open — November 2, 2026 |
| Keycard Go #20 | Open; fix absent from upstream develop |

Do not infer inclusion in an official SDK release
from the existence of a fix commit alone.

## Baseline Tests

From the Kohaku CLI implementation repository:

    npm test
    npm run typecheck
    npm run build

Record:

- Test count: 538
- Passed: 538
- Failed: 0
- Build result: PASS
- Commit: 4c7aa87
- Date: November 2, 2026

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

- [x] Upstream status verified.
- [ ] SDK and CLI versions recorded.
- [x] Existing tests pass.
- [x] Production build passes.
- [ ] Physical signer baseline passes.
- [ ] Threat model reviewed.
- [ ] Sepolia dependencies identified.
- [ ] V2 implementation branch created.

## Findings

### November 2, 2026 — Software baseline

- 538 regression tests passed with zero failures.
- TypeScript typecheck passed.
- Production build passed.
- Research checkpoint: ca8ec61.
- CLI checkpoint: 4c7aa87.
- Local SDK checkout contains fix f64e791.
- Upstream Keycard Go PR #20 remains open.
- Upstream develop still contains the original buffer-aliasing code.
- Kohaku CLI PRs #67, #68, and #69 remain open.
- Official Keycard SDK/CLI release containing the fix is unverified.

The existing physical-hardware tests remain valid historical
V1 evidence. Fresh V2 hardware and device-session checks
are still pending.

### Remaining Iteration 0 work

- Verify Keycard CLI binary provenance and versions.
- Revalidate the physical Keycard signing path.
- Review PIN and device-session implementation.
- Finalize the threat model.
- Verify Sepolia execution dependencies.

## Decision

Iteration 0 gate: OPEN.
