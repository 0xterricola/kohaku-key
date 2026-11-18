# Kohaku Key — Threat Model

**Updated:** November 5, 2026

**Scope:** Verified V1/V2/V3 research boundaries and proposed V4 experiments. No independent security audit is claimed.

## Protected assets

Ethereum signing keys, Keycard PINs, transaction intent, delegation scope, submission state, BIP-85-derived material, privacy credentials, nullifiers, private witnesses and recovery metadata.

## Threats

Host malware, malicious RPC or bundler data, swapped devices, malicious firmware, replayed transactions, duplicate submission, device loss, incorrect note recovery and on-chain metadata correlation.

## Verified boundaries

**Keycard:** Ethereum signing keys remained on the physical device during tested operations. The ordinary retail card did not independently display full transaction intent.

**Host:** Prepared and approved transaction intent and performed V3 credential derivation, witness calculation and Groth16 proving. Host compromise remains in scope.

**RPC and blockchain state:** Expected roots, receipts and events were checked through two providers. Provider agreement is not independent consensus verification.

**Privacy protocol:** V3 demonstrated the Privacy Pools V1 deposit, withdrawal, recovery and simulated subsequent spend. Direct withdrawal exposed account linkage.

**Recovery:** Fresh authenticated sessions reproduced the tested note. Replacement-device recovery remains unverified.

**Submission safety:** V2 journal and duplicate-submission protections operated on the tested transaction or UserOperation identity. They do not prevent a distinct operation created with a new nonce, nor guarantee exactly-once execution after arbitrary failures.

## Unverified protections

- Compromised-host resistance for privacy credentials and witnesses.
- Shell firmware authenticity and credential isolation in a Kohaku-specific implementation.
- Hardware-contained witness generation or Groth16 proving.
- Unlinkability of the demonstrated direct withdrawal.
- Tornado Cash, RAILGUN or Privacy Pools V2 hardware interoperability.
- Full device-loss recovery and an independent security audit.

## V4 security gate

Before using Shell as a credential boundary, test firmware integrity, debugging interfaces, sensitive-memory handling, device communication, recovery behavior and permitted outputs.

If private witness material moves to an external prover, that prover becomes part of the trusted computing base.

[Security and recovery](SECURITY-AND-RECOVERY.md) | [Current status](PROJECT-STATUS.md) | [V3 report](V3-FINAL-RESEARCH-REPORT.md)
