# kohaku-key

Independent research into hardware-backed Ethereum execution, privacy
credential recovery, and cryptographic operations on secure elements.

**Experimental research, not production-ready or security-audited.**
Not an official release of the Ethereum Foundation, Kohaku, Keycard,
Privacy Pools, or RAILGUN.

## Research projects

| Project | Scope |
| --- | --- |
| [Privacy Pools V1](privacy-pools-v1/README.md) | V1–V4 Keycard signing, deterministic credential recovery, Shell QR integration, Sepolia demonstrations, and security limitations |
| [RAILGUN](RAILGUN/README.md) | JCOP3 BabyJubJub, PACE-GM, BN254/Poseidon investigations, and cross-generation hardware benchmarking |

## Upstream contributions

Research findings are contributed upstream separately. These PRs are
not equivalent to production support or acceptance by maintainers.

| Upstream PR | Research outcome | Status (2026-11-18) |
| --- | --- | --- |
| [Ethereum Kohaku #382](https://github.com/ethereum/kohaku/pull/382) | Privacy Pools V1 sparse deposits, explicit deposit indices, and recovery-state handling | Open; under review |
| [Kohaku CLI #67](https://github.com/kassandraoftroy/kohaku-cli/pull/67) | External viem signers for Ethereum/EIP-7702 | Open |
| [Kohaku CLI #68](https://github.com/kassandraoftroy/kohaku-cli/pull/68) | Experimental offline Keycard transaction signing | Open; depends on #67 |
| [Kohaku CLI #69](https://github.com/kassandraoftroy/kohaku-cli/pull/69) | Offline Keycard-backed EIP-7702 UserOperation signing | Open; depends on #67/#68 |
| [Keycard Go #20](https://github.com/keycard-tech/keycard-go/pull/20) | Fix legacy ECDSA signature buffer corruption found during physical signing tests | Merged into develop |
| [Keycard Shell #234](https://github.com/keycard-tech/keycard-shell/pull/234) | Privacy Pools V1 BIP-85 derivation, encrypted QR export, and public Sepolia demonstration | Closed without merge; research archived |

### Privacy Pools V1 hardware boundary

Keycard Shell #234 was closed on November 13, 2026 after reviewing
the security expectations of official hardware-wallet features.
The functional Sepolia deposit, withdrawal, and recovery demonstration
succeeded, but Privacy Pools V1 requires sensitive note material on
the host for zero-knowledge proof generation.

Encrypted transport and protected master-key custody do not provide
end-to-end hardware isolation. No further upstream merge work is planned
for that experimental Shell integration in its present architecture.

## RAILGUN hardware testing

- [Physical benchmark results](RAILGUN/benchmarks/RESULTS.md)
- [JavaCard sources and CAPs](RAILGUN/applets/README.md)
- [Portable JavaCard build instructions](RAILGUN/applets/BUILDING.md)
- [Public PACE test vectors](RAILGUN/vectors/PUBLIC-PACE-VECTORS.json)
- [Offline verification script](RAILGUN/scripts/benchmark.py)
- [Hardware developer setup](RAILGUN/experiments/physical-benchmark-runner/README.md)

JCOP3 physical results are recorded. JCOP4 and JCOP4.5 performance and
applet compatibility remain unverified. Published CAPs are experimental
research artifacts, not firmware releases or universal installations.

## Development workflow

New investigations start under `RAILGUN/experiments/`. Validated
implementations move to `applets/` or `scripts/`; measurements and
methodology move to `benchmarks/`.

Never commit private keys, seed phrases, pairing secrets, raw sensitive
APDU captures, proprietary SDKs, or personal hardware diagnostics.
