# Kohaku Key — V2 Security Model

**Status:** Draft — Iteration 0
**Created:** November 2, 2026

## 1. Assets

Protect:

- Hardware Ethereum signing key.
- Keycard PIN and unlock credentials.
- Transaction and delegation intent.
- Signing-session identity.
- UserOperation nonce and fee parameters.
- Submission and recovery state.
- Wallet backup and recovery information.

## 2. Trust Boundaries

### Physical Keycard

Trusted for private-key custody and cryptographic
signing within its supported firmware behavior.

Not assumed to provide independent transaction
display or transaction-policy validation.

### Host application

Trusted for transaction preparation, display,
user confirmation, and supplying the signing digest.

A compromised host can misrepresent intent.

Host-side approval is not equivalent to
independent hardware transaction verification.

### Keycard SDK and transport

The parser, APDU transport, and device-session
logic are security-critical.

Validate signature integrity and signer recovery.

The legacy ECDSA parser aliasing bug discovered
during V1 illustrates this dependency risk.

### Ethereum RPC

Treat returned chain state, nonces, fees, receipts,
and delegation information as untrusted input.

Check chain identifiers and verify results
against the expected operation.

### ERC-4337 bundler

Treat gas estimates, simulation results,
submission responses, and receipts as untrusted.

Verify operation identity and resulting
Ethereum transaction state.

## 3. Threats and Controls

| Threat | Proposed control |
|---|---|
| PIN exposed through environment | Interactive secret entry |
| PIN exposed in logs | Redaction and negative tests |
| Wrong Keycard connected | Address and account verification |
| Reader removed during signing | Session cancellation |
| Duplicate signing requests | Serialized device session |
| Wrong chain | Explicit chain validation |
| Transaction field mutation | Approved-intent binding |
| Malicious EIP-7702 delegate | Trusted code/target policy |
| Untrusted RPC values | Input validation and verification |
| Bundler rejection | Explicit error classification |
| Unknown submission status | Reconciliation before retry |
| Duplicate execution | Persisted operation identity |
| Compromised host | Document limitation; evaluate trusted display |

## 4. PIN Handling

V1's KEYCARD_PIN environment variable is a
prototype limitation.

V2 must avoid passing PINs through:

- Command-line arguments.
- Environment variables.
- Persistent configuration.
- Logs and diagnostics.
- Exception messages.

Interactive secret handling should minimize
memory lifetime and avoid unnecessary copies.

Host-memory compromise cannot be eliminated
solely through interactive PIN entry.

## 5. Transaction Approval

Approval must bind to:

- Network and chain ID.
- Sender and destination.
- Value and calldata.
- Transaction type.
- Nonce and fees.
- EIP-7702 delegation target, when present.
- UserOperation call list and gas parameters.

If the approved operation changes, require
a new review and confirmation.

Signing and submission require separate
explicit decisions.

## 6. EIP-7702 Security

EIP-7702 delegation can modify EOA execution
behavior.

Requirements:

- Verify on-chain delegation state.
- Verify expected implementation code.
- Restrict approved delegate targets.
- Validate authorization chain ID and nonce.
- Display delegation effects separately.
- Require approval for new delegation.
- Reject chain-independent authorizations
  under the V2 policy.
- Check delegation state after execution.

## 7. Recovery Safety

Persist non-secret operation metadata before
submission.

Reconcile uncertain outcomes before any retry.

Never assume a timeout means an operation
was not submitted or included.

Do not silently create replacement signatures.

## 8. Explicitly Unsupported Claims

V2 does not establish:

- Mainnet production readiness.
- Resistance to a compromised host.
- Independently verified hardware display.
- Unrestricted EIP-7702 delegation safety.
- Privacy Pools note-secret protection.
- ZK credential isolation.
- Hardware-isolated proof generation.

## 9. Open Security Decisions

- Official SDK versus locally verified build.
- PIN transport and session interface.
- Device-session cancellation semantics.
- Approved-intent representation.
- Delegation implementation allowlist.
- RPC and bundler verification strategy.
- Persistent operation-state format.
- Transaction replacement/retry policy.
- Trusted-display research direction.

Resolve these during the corresponding
V2 implementation parts.

## 10. Review Gate

Iteration 0 security review:

- [ ] Assets confirmed.
- [ ] Trust boundaries confirmed.
- [ ] SDK parser provenance checked.
- [ ] PIN handling design selected.
- [ ] Delegation policy defined.
- [ ] Unknown submission policy defined.
- [ ] Known unsupported guarantees recorded.
