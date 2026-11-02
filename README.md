# Kohaku Key

Hardware-backed Ethereum signing and privacy credential research
for Kohaku CLI.

## V1 goals
1. Verify Keycard signature determinism.
2. Refactor Kohaku CLI public signing to use viem accounts.
3. Implement a Keycard-backed Ethereum signer.
4. Investigate Privacy Pools EnvelopeSigner compatibility.

## Repositories
- Research: kohaku-key (this repository)
- Upstream: https://github.com/kassandraoftroy/kohaku-cli

## Scope
Existing Keycard hardware first. No custom hardware,
new privacy vault, or Railgun key isolation in V1.

See docs/ for roadmap, architecture, and security boundaries.

<!-- kohaku-status:start -->
## Implementation status — November 2, 2026

**V1 offline hardware-signing prototype: complete.**

Verified on retail Keycard 3.1:

- EIP-191 message signing
- EIP-712 typed-data signing
- EIP-1559 transactions
- EIP-7702 authorizations
- Simple7702 ERC-4337 UserOperations

Kohaku CLI integration provides offline EIP-1559 signing and
two-or-more-call Simple7702 batch signing through
`transact-raw --signer keycard`.

**Validation:** 538/538 Kohaku CLI tests passing, TypeScript
typecheck passing, production build passing, and physical
Keycard signing verified. No RPC calls or broadcasts occurred
in the offline hardware UserOperation test.

**Upstream contributions:**

- [Kohaku CLI #67](https://github.com/kassandraoftroy/kohaku-cli/pull/67) — external viem signers
- [Kohaku CLI #68](https://github.com/kassandraoftroy/kohaku-cli/pull/68) — Keycard EIP-1559 integration
- [Kohaku CLI #69](https://github.com/kassandraoftroy/kohaku-cli/pull/69) — offline Simple7702 batch signing
- [Keycard Go #20](https://github.com/keycard-tech/keycard-go/pull/20) — legacy ECDSA parser fix; upstream inclusion requires verification

**Research documentation:**

- [V1 outcome and acceptance status](docs/V1-OUTCOME.md)
- [Project status](docs/PROJECT-STATUS.md)
- [Security and recovery findings](docs/SECURITY-AND-RECOVERY.md)
- [Reproducing experiments](docs/REPRODUCIBILITY.md)

The original proposal's live Sepolia broadcast criterion remains
unmet. Privacy Pools signature-derived recovery was investigated
but not established. This is not a production-ready wallet.
<!-- kohaku-status:end -->
