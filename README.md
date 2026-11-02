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
## Implementation status

Hardware signing has been validated using a retail
Keycard 3.1 and viem 2.55.19.

EIP-191, EIP-712, EIP-1559, EIP-7702 authorization,
and offline Simple7702 UserOperation signing are verified.

Kohaku CLI now has an experimental, offline-only
`transact-raw --signer keycard` implementation.

**Upstream contributions:**

- [Keycard Go #20](https://github.com/keycard-tech/keycard-go/pull/20) — merged SDK ECDSA fix
- [Kohaku CLI #67](https://github.com/kassandraoftroy/kohaku-cli/pull/67) — external viem signer refactor
- [Kohaku CLI #68](https://github.com/kassandraoftroy/kohaku-cli/pull/68) — hardware signing integration

**Research and limitations:**

- [Project status](docs/PROJECT-STATUS.md)
- [Security and recovery findings](docs/SECURITY-AND-RECOVERY.md)
- [Reproducing experiments](docs/REPRODUCIBILITY.md)

The prototype is not production-ready. Live broadcasting
and independent on-device transaction confirmation are
not implemented.
<!-- kohaku-status:end -->
