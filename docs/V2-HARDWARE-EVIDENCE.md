# Kohaku Key V2 — Native Hardware Evidence

Date: November 2, 2026

## Implementation

- Repository: 0xterricola/kohaku-cli
- Branch: feat/v2-device-session
- Native bridge: c631355
- CLI integration: ec9aeca
- SDK: local patched keycard-go checkout
- Hardware: retail Keycard 3.1, OMNIKEY reader
- Derivation: m/44'/60'/0'/0/0

## Hardware verification

Expected and recovered address:
0xB8A0f79E6d64c948E9F5ea32aD93647777915EBa

- Native interactive PIN authentication: PASS
- Hardware public-key export: PASS
- EIP-191 signature and viem recovery: PASS
- Offline EIP-1559 hardware signing: PASS
- Offline EIP-7702 UserOperation generation: PASS
- Native bridge missing-binary exit code: PASS
- No KEYCARD_PIN or --pin transport: VERIFIED
- No transaction broadcasting performed

EIP-1559 test chain: 31337
EIP-1559 test nonce: 0
EIP-1559 transaction hash:
0xd3d6d0d64e15fa184020740e7a54eb1b92ac36735d3f1c1fc3001d7a89e7ef8f

## Regression baseline

- JavaScript tests: 540 passed, 0 failed
- Go bridge tests: PASS
- TypeScript typecheck: PASS
- Production build: PASS

## Remaining work

- Transaction intent preparation and explicit approval
- Device disconnect, cancellation, and PIN failure tests
- Multiple-reader selection policy
- Standard Node.js ESM startup compatibility
- Sepolia transaction submission and receipts

These results establish offline hardware operation only.
They do not establish production readiness or live
testnet execution.
