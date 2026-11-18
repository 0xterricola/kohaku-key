> **Historical snapshot — November 2, 2026.** Preserved from commit `e9b989b`. See the current README and project status for updated milestone conclusions.

---

# Kohaku Key — V1 Research Outcome

Updated: November 2, 2026

## Status

**Offline hardware-signing prototype: complete.**

**Original end-to-end V1 acceptance: not yet complete.**

The original proposal required broadcasting a Keycard-signed
transaction on Sepolia. The work completed to date deliberately
remains offline and does not satisfy that specific criterion.

## Verified capabilities

Retail Keycard applet 3.1 with an OMNIKEY reader:

- EIP-191 UTF-8 and raw-byte signing
- EIP-712 typed-data signing
- EIP-1559 transaction signing
- EIP-7702 authorization signing
- Simple7702 ERC-4337 UserOperation signing
- Signature verification and Ethereum address recovery

Kohaku CLI integration additionally verifies an offline
two-call Simple7702 UserOperation through
`transact-raw --signer keycard --keycard-userop`.

No private signing key export, RPC access, bundler submission,
or on-chain transaction occurred in the offline tests.

## Validation checkpoint

- 538/538 Kohaku CLI regression tests passed
- TypeScript typecheck passed
- Production build passed
- Physical Keycard two-call CLI signing passed
- Recovered signer matched the card's Ethereum account
- Altered chain ID failed typed-data signature verification
- Zero RPC requests in offline UserOperation verification

Source branch: `0xterricola/kohaku-cli:feat/keycard-7702-userop`

Checkpoint commits:
`9da4fdf`, `42b29e8`, `0fa841d`, `4c7aa87`.

## Upstream contributions

- [Kohaku CLI #67](https://github.com/kassandraoftroy/kohaku-cli/pull/67):
  external viem signing account support
- [Kohaku CLI #68](https://github.com/kassandraoftroy/kohaku-cli/pull/68):
  offline Keycard EIP-1559 signing
- [Kohaku CLI #69](https://github.com/kassandraoftroy/kohaku-cli/pull/69):
  offline Keycard Simple7702 UserOperations
- [Keycard Go #20](https://github.com/keycard-tech/keycard-go/pull/20):
  ECDSA parser aliasing fix, commit `c4cf5cc`

The three Kohaku CLI pull requests are stacked and awaiting
upstream review. #69 depends on #68, which depends on #67.

The Keycard Go fix commit is available, but the current public
`develop` branch and PR status appeared inconsistent with the
earlier merge report on November 2, 2026. Verify branch inclusion
before relying on an upstream SDK/CLI version.

## Security boundaries

- The tested retail Keycard blindly signs host-supplied digests.
- The PIN is passed through an environment variable in the prototype.
- EIP-7702 authorization signatures were tested, but delegation
  was not activated.
- The offline UserOperation has caller-provided nonce and gas fields.
- It is not submission-ready and includes no delegation authorization.
- No live bundler, testnet receipt, or production workflow was tested.
- No independently verified on-device transaction approval exists.
- Keycard Shell was not validated in these experiments.

## Privacy credential research

The Keycard developer confirmed randomized native JavaCard
ECDSA nonces. This mode does not provide reproducible signature
bytes for deterministic Privacy Pools note-secret derivation.

The original SDK parser defect also invalidated signatures
observed in early experiments. The deterministic-credential
path is therefore deferred rather than treated as implemented.

Ethereum signing-key isolation does not establish isolation
of privacy-note secrets or ZK proving credentials.

## Remaining acceptance work

Upstream review and merge, secure PIN/device handling,
transaction approval, official SDK verification, network-backed
EIP-7702 preparation and authorization checks, and successful
testnet submission and receipt verification remain outstanding.

This document closes the **offline research milestone**, not
the production security or original live-transaction milestone.
