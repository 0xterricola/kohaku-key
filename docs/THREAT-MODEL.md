# Kohaku Key — Threat Model

**Applies to:** V1/V2 research evidence and proposed V3 privacy experimentation. No production security audit is claimed.

## Assets and adversaries

Protect Ethereum signing keys, Keycard PINs, reviewed transaction intent, delegation scope, submission state, privacy credentials and recovery material. Consider host malware, a malicious RPC/bundler, a swapped/removed card, application restart, device loss, wrong chain/delegate, replay/duplicate operations and host-side proving disclosure.

## Trust boundaries

- **Card:** Verifiable possession of Ethereum private signing key; ordinary retail card does not independently show approved transaction fields.
- **Host:** Constructs transaction/userop digests, displays approval and handles I/O. Host compromise is not solved by cryptographic signature verification.
- **RPC / bundler:** Supply potentially stale or misleading chain data and submission results. Confirm against expected hashes and on-chain events.
- **Privacy SDK / prover:** May require notes, witnesses, viewing or spending material outside hardware. Determine this per protocol, not by analogy to public Ethereum signing.
- **Backup/recovery:** Same Ethereum address is not proof of same privacy note; test exact derivation and recovery contract.

## Existing controls and gaps

V2 establishes approval gates, nonce/chain/delegation checks, calldata binding, signer recovery, journal-first transmission and receipt reconciliation for a Sepolia proof of concept. It does not establish trusted-device display, host compromise resistance, guaranteed exactly-once execution for newly generated nonces, production-grade secure memory, real-crash restart behavior or privacy-note isolation.

## V3 security gates

Before deriving or funding privacy credentials, require demonstrated primitive availability, domain-separated reproducibility, verified protocol outputs, restart/replacement recovery and a full host-exposure map. For ECDH, determine who holds private keys and who sees the shared secret. For BIP-85, determine exact permitted entropy derivation, device support and backup behavior. No mainnet or real-value testing.
