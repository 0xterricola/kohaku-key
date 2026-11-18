# Kohaku Key — Security and Recovery Findings

**Updated:** November 5, 2026

## V1 — Signing

The tested retail Keycard produced randomized ECDSA signatures.

An earlier Keycard Go signature-parser issue was investigated and corrected locally. The initial environment-based PIN transport was replaced during later research.

[Keycard Go investigation](https://github.com/keycard-tech/keycard-go/pull/20)

## V2 — Execution controls

The V2 Sepolia experiments demonstrated:

- Physical Keycard signing and identity verification.
- Explicit transaction and authorization approvals.
- Chain, nonce, delegation, calldata and signer validation.
- Journal-first transaction submission.
- Independent receipt and on-chain event reconciliation.
- Failure and uncertain-submission regression tests.

These controls do not establish a trusted on-device display or resistance to a malicious host.

The V2 journal was written before a send attempt, and duplicate submission checks applied to the same UserOperation hash. A different nonce can create a distinct operation; exactly-once execution is not guaranteed.

Uncertain-submission and automatic-reconciliation cases were exercised in mocked regression tests. The actual Sepolia journal was manually reconciled. No physical forced-process-crash recovery drill was performed.

## V3 — Privacy Pools V1

The verified research demonstrated:

- Reproducible BIP-85-derived credentials across authenticated hardware sessions.
- Versioned HMAC-based credential derivation and note lineage.
- Host-memory witness calculation and independently verified Groth16 proofs.
- Separate SIGN and BROADCAST approvals for the real withdrawal.
- Verification of the mined nullifier and change commitment.
- Fresh hardware recovery of the on-chain change note.
- Updated Merkle inclusion and a second valid withdrawal simulation.

Private witness and credential material was not intentionally persisted to research evidence files.

This does not prove complete erasure from host memory or protection against side channels.

Actual on-chain Groth16 proof calldata is publicly observable.

## Recovery constraints

Successful recovery depends on preserving:

- The BIP-85 derivation path and device-root availability.
- The versioned HMAC domain and derivation contract.
- Chain, entrypoint, account and deposit indexes.
- Withdrawal indexes and note lineage.
- The note label, value and relevant historical chain state.

Fresh-session recovery was demonstrated. Complete replacement-card recovery was not.

Changing derivation schemes or reassigning indexes can make historical notes unrecoverable.

## Remaining security boundaries

The V3 root, private credentials and Groth16 computation entered the host environment.

The tested direct withdrawal exposed public account linkage.

V4 investigates keeping sensitive credential operations inside Shell, but no Kohaku-specific Shell isolation guarantee has been verified.

[Threat model](THREAT-MODEL.md) | [V3 report](V3-FINAL-RESEARCH-REPORT.md) | [Current status](PROJECT-STATUS.md)
