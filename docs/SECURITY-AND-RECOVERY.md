# Kohaku Key — Security and Recovery Findings

**Consolidated:** November 2, 2026. The earlier V1 offline prototype limitations are historical; the V2 Sepolia PoC does not imply production readiness.

## V1 lessons

- The Keycard Go ECDSA parser initially mishandled signature-buffer aliasing; hardware verification and recovery were retested with a corrected local build. See [Keycard Go #20](https://github.com/keycard-tech/keycard-go/pull/20).
- Native card ECDSA signatures are randomized, so identical message signing does not prove reproducible note credentials.
- The earliest CLI prototype used environment-based PIN transport; it was not a secure device-session design.

## V2 controls demonstrated

- Native Keycard interface with interactive PIN, identity verification and safe failure tests.
- Explicit EIP-7702 authorization, UserOperation signature and final submission approvals.
- Revalidation of chain, EOA and UserOperation nonces, delegated implementation, intended calldata and signing digest.
- A journal written before one send attempt; same-hash duplicate submissions rejected.
- Independent Sepolia receipt, EntryPoint event and delegation checks; actual journal reconciled to `confirmed`.
- Mocked tests for uncertain submissions, malformed results and automatic reconciliation failures.

## Boundaries and remaining work

The tested retail Keycard signs host-provided digests without displaying their semantic content. A compromised host can still misrepresent intent. A process restart with an uncertain submission was modeled in tests, but no real forced-crash drill was performed. Duplicate prevention applies to the same UserOperation hash; a new nonce can produce a different operation.

V3 privacy credentials require a separate recovery analysis. Neither Ethereum private-key custody nor ECDH key agreement alone demonstrates that note secrets or ZK witnesses never reach host memory. Test device loss, supported backup recovery, domain separation, context-specific key use and verifier compatibility before any funded privacy deposits.

See the [threat model](THREAT-MODEL.md), [V2 evidence](V2-TESTNET-RESULTS.md), and [V3 research plan](V3-PROPOSAL.md).
