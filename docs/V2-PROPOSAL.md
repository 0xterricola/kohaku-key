# Kohaku Key — V2 Technical Proposal

## Secure Hardware-Backed Ethereum Execution

**Status:** Proposed
**Created:** November 2, 2026
**Research:** https://github.com/0xterricola/kohaku-key
**Implementation:** https://github.com/kassandraoftroy/kohaku-cli

---

## 1. Overview

V2 advances the verified V1 offline hardware-signing
prototype into a testnet execution system.

The objective is to prepare, review, sign, submit, confirm,
and recover Ethereum operations using a physical Keycard.

V2 reuses the V1 viem-compatible signer rather than
reimplementing cryptographic signing.

### Primary goal

Execute and confirm on Sepolia:

1. A Keycard-signed EIP-1559 transaction.
2. A two-call Keycard-signed Simple7702 ERC-4337
   UserOperation with validated EIP-7702 delegation.

Neither operation may require importing a software
private key or mnemonic into Kohaku CLI.

This is a testnet research milestone, not a claim
of production wallet security.

---

## 2. V1 Foundation

The following capabilities were verified:

- Physical Keycard ECDSA signing.
- EIP-191 message signing.
- EIP-712 typed-data signing.
- EIP-1559 transaction signing.
- EIP-7702 authorization signing.
- Simple7702 ERC-4337 UserOperation signing.
- Viem LocalAccount integration.
- Offline transaction and batch signing through Kohaku CLI.
- Ethereum address recovery and signature verification.
- Zero-RPC offline hardware signing.

The final Kohaku CLI checkpoint passed 538 tests,
TypeScript typecheck, production build, and physical
two-call UserOperation verification.

### Related upstream work

- Kohaku CLI #67: External viem signer support.
- Kohaku CLI #68: Offline Keycard transaction signing.
- Kohaku CLI #69: Offline Keycard Simple7702 signing.
- Keycard Go #20: Legacy ECDSA signature parser fix.

Current upstream integration and release status must
be verified as part of Iteration 0.

### Unfinished V1 acceptance

The original Sepolia transaction broadcast acceptance
criterion was not completed.

V2 explicitly carries it forward into Part 3.

Privacy Pools signature-derived credential recovery
remains deferred due to randomized native ECDSA.

---

## 3. Architecture

```text
Transaction Intent
    |
    v
Preparation
    - RPC chain validation
    - Nonce resolution
    - Fee estimation
    - Delegation state
    - Simulation
    |
    v
Review and Policy
    - Transaction summary
    - Delegation verification
    - Explicit approval
    |
    v
Hardware Signing
    - viem LocalAccount
    - Keycard session
    - PIN authentication
    - APDU signing
    |
    v
Execution
    - Ethereum RPC
    - ERC-4337 bundler
    |
    v
Verification and Recovery
    - Transaction receipt
    - UserOperation receipt
    - On-chain state
    - Persistent operation status
```

### Architecture requirements

- Preserve the existing V1 offline signing path.
- Keep transaction preparation separate from signing.
- Keep signing separate from submission.
- Never expose the hardware private key.
- Require approval before hardware signing.
- Verify signer identity and chain consistency.
- Reject unsupported EIP-7702 delegation targets.
- Never automatically retry an uncertain submission.
- Preserve existing software-signer compatibility.
- Leave privacy keystore and deriveAt interfaces unchanged.

---

## 4. Development Roadmap

### Iteration 0 — Baseline and Threat Model

**Objective:** Establish a reproducible V2 starting point.

Implementation:

- Verify upstream status of PRs #67, #68, and #69.
- Verify Keycard Go #20 and SDK fix provenance.
- Record exact local software and hardware versions.
- Run all existing Kohaku CLI regressions.
- Verify the physical Keycard signing baseline.
- Document trusted and untrusted components.
- Establish Sepolia environment requirements.
- Identify current device and PIN handling weaknesses.
- Create the V2 development branch.

Deliverables:

- `docs/V2-BASELINE.md`
- `docs/V2-SECURITY-MODEL.md`
- Verified V2 implementation branch.

Acceptance:

- Existing tests and build pass.
- Hardware signing remains functional.
- Dependencies and versions are documented.
- The threat model identifies the trust boundaries.
- No V1 implementation regressions.

---

### Part 1 — Secure Keycard Device Interface

**Objective:** Harden the hardware signing lifecycle.

Implementation:

- Define a device/session abstraction.
- Replace KEYCARD_PIN environment-variable handling.
- Implement interactive secret entry.
- Prevent PIN exposure through arguments and logs.
- Minimize secret lifetime in process memory.
- Verify connected card identity.
- Support derivation-path selection.
- Handle device connection and removal.
- Handle invalid PINs and blocked PIN states.
- Support signing cancellation and timeouts.
- Prevent concurrent operations on the same reader.
- Preserve the viem account interface.

Deliverables:

- Device-session implementation.
- Device lifecycle tests.
- Physical hardware validation.

Acceptance:

- No environment-variable PIN required.
- No PIN appears in CLI arguments or logs.
- Expected signer address is verified.
- Device removal fails safely.
- Cancellation stops the signing operation.
- Offline V1 signing continues working.

Gate:

No new online signing path until device-session
behavior is verified.

---

### Part 2 — Transaction Preparation and Review

**Objective:** Validate and review transaction intent
before requesting a hardware signature.

Implementation:

- Define a structured transaction-intent model.
- Resolve and validate RPC chain ID.
- Obtain pending EOA transaction nonce.
- Estimate EIP-1559 gas and fees.
- Display chain, sender, recipient, value, and calldata.
- Decode known ABI calls when trustworthy ABI data exists.
- Label unknown calldata as unverified.
- Display estimated and maximum transaction costs.
- Require explicit approval before signing.
- Prevent mutation of approved transaction parameters.
- Preserve the offline-only execution path.

Deliverables:

- Transaction preparation layer.
- Review and confirmation interface.
- Policy and transaction-mutation tests.

Acceptance:

- Chain mismatch blocks signing.
- Recipient or value changes require renewed approval.
- Fee and calldata changes require renewed approval.
- User cancellation produces no signature.
- Preparation does not submit anything.

Limitation:

Host-side transaction review is not independent
hardware-display verification.

---

### Part 3 — Sepolia EIP-1559 Execution

**Objective:** Complete the original V1 live
transaction acceptance criterion.

Implementation:

- Add an explicitly enabled online Keycard mode.
- Resolve nonce, gas, fees, and chain from Sepolia.
- Review the complete transaction.
- Sign using the physical Keycard.
- Recover and verify the Ethereum signer.
- Persist transaction identity before broadcasting.
- Broadcast through Ethereum RPC.
- Monitor transaction hash and receipt.
- Verify chain, status, sender, destination, and confirmations.
- Handle interrupted receipt monitoring.
- Prevent accidental duplicate submission.

Deliverables:

- Successful Sepolia transaction.
- Recorded transaction hash and receipt.
- Reproducible test procedure.

Acceptance:

- Physical Keycard signs the transaction.
- Software mnemonic/private key is never loaded.
- Sepolia broadcast succeeds.
- Receipt confirms successful execution.
- Transaction signer and chain match expectations.
- Interrupted monitoring can resume safely.

Milestone:

**First confirmed Keycard-signed Sepolia transaction.**

---

### Part 4 — EIP-7702 Delegation and Preparation

**Objective:** Safely prepare live Simple7702
UserOperations with explicit delegation policy.

Implementation:

- Read current EIP-7702 delegation state.
- Verify the expected Simple7702 implementation.
- Pin trusted implementation addresses or code hashes.
- Distinguish EOA nonce from EntryPoint nonce.
- Resolve ERC-4337 nonce and nonce key.
- Prepare UserOperations using viem and a bundler.
- Estimate gas and fees using network-aware data.
- Simulate UserOperation validation.
- Display every call, destination, and value.
- Determine whether delegation authorization is required.
- Construct chain-bound delegation authorizations.
- Review delegation target before authorization signing.
- Reject unapproved implementation addresses.
- Reject chainId 0 authorizations under V2 policy.
- Separate already-delegated and new-delegation paths.

Deliverables:

- Network-aware UserOperation preparation.
- Delegation policy.
- Simulation and rejection tests.

Acceptance:

- Existing delegation state is verified.
- Trusted implementation checks pass.
- EntryPoint nonce is resolved correctly.
- Bundler preparation and simulation succeed.
- Delegation requires explicit approval.
- Unauthorized delegation targets are rejected.
- No submission occurs during review.

Gate:

No live UserOperation submission until delegation
and simulation controls pass.

---

### Part 5 — Live ERC-4337 UserOperation Execution

**Objective:** Submit and confirm a two-call
hardware-signed Simple7702 operation on Sepolia.

Implementation:

- Construct and verify the final UserOperation.
- Sign using the physical Keycard.
- Recover and verify the expected owner.
- Persist operation identity before submission.
- Submit through a supported bundler.
- Track the UserOperation hash.
- Obtain the resulting transaction hash.
- Verify UserOperation and transaction receipts.
- Verify execution success and resulting state.
- Recheck EIP-7702 delegation state.
- Test both existing and initial delegation.
- Prevent unintended retries after timeouts.

Deliverables:

- Successful two-call Sepolia UserOperation.
- Verified UserOperation and transaction receipts.
- Documented delegation and execution evidence.

Acceptance:

- Both calls execute successfully.
- Keycard signer matches the account owner.
- Delegation is approved and verified.
- Bundler submission succeeds.
- Receipts confirm successful execution.
- Expected on-chain state is observed.
- No software signing key is imported.

Milestone:

**First confirmed Keycard-signed Simple7702 batch.**

---

### Part 6 — Reliability and Recovery

**Objective:** Make interrupted and failed
operations recoverable without unsafe resubmission.

Define persistent operation states:

- Prepared
- Approved
- Signed
- Submitted
- Included
- Confirmed
- Failed
- Unknown

Implementation:

- Persist non-secret operation metadata.
- Resume receipt monitoring after restart.
- Reconcile unknown submission outcomes.
- Detect stale EOA and EntryPoint nonces.
- Handle RPC errors and timeouts.
- Handle bundler rejection.
- Handle execution reverts.
- Handle reader removal during signing.
- Handle invalid PIN and cancellation.
- Prevent unintended duplicate signing/submission.
- Add fault-injection tests.
- Retest software-signer compatibility.

Deliverables:

- Recovery-state implementation.
- Failure-injection regression suite.
- Recovery and troubleshooting documentation.

Acceptance:

- Interrupted operations can be inspected.
- Known submissions are not silently replaced.
- Unknown outcomes require reconciliation.
- Signing secrets are never persisted.
- Existing software wallet functionality remains intact.

---

## 5. Optional Research — Keycard Shell

Investigate whether Keycard Shell provides stronger
device-side transaction verification.

Research questions:

- Which transaction fields are independently displayed?
- Does the displayed intent bind to the signed digest?
- Can QR transport reuse the existing viem signer?
- What additional trust assumptions are introduced?
- Does Shell improve approval security versus retail Keycard?

Deliverable:

Separate hardware approval and compatibility report.

This research is not required to complete V2.

---

## 6. Security Requirements

### Hardware key isolation

The Ethereum signing private key remains on Keycard.

### PIN protection

PINs must not be passed through CLI flags,
environment variables, logs, or persistent files.

### Explicit approval

The host must display and request approval for
the exact transaction or operation being signed.

### EIP-7702 controls

Delegation addresses, implementation code,
chain ID, and authorization nonce must be validated.

### Network boundaries

RPC providers and bundlers are untrusted sources
of data requiring validation where possible.

### Reliable execution

Signing and submission must be separate operations.

Uncertain submission results must not trigger
automatic replacement or duplicate submission.

### Trust limitation

Retail Keycard does not provide independent trusted
transaction display. A compromised host remains
a relevant threat.

---

## 7. Scope

Included:

- Retail Keycard hardware signing.
- Device and PIN lifecycle hardening.
- Transaction preparation and review.
- Sepolia EIP-1559 execution.
- Sepolia EIP-7702 authorization and delegation.
- Simple7702 ERC-4337 execution.
- Bundler integration.
- Receipt verification.
- Error handling and recovery.
- Hardware and automated tests.
- Documentation and upstream contributions.

Excluded:

- Ethereum mainnet execution.
- Production wallet certification.
- Arbitrary EIP-7702 delegate support.
- Privacy Pools credential recovery.
- Railgun spending-key management.
- Hardware-isolated ZK proving.
- Casberi and mobile integration.
- Unattended hardware signing.
- Required Keycard Shell support.

---

## 8. Research and Implementation

### kohaku-key

Research repository:

- `docs/V2-PROPOSAL.md`
- `docs/V2-BASELINE.md`
- `docs/V2-SECURITY-MODEL.md`
- `docs/V2-TESTNET-RESULTS.md`
- `docs/V2-OUTCOME.md`

Maintain implementation findings, design decisions,
experiment results, and security boundaries here.

### kohaku-cli

Implementation repository.

Proposed workstreams:

| ID | Workstream |
|---|---|
| V2-A | Device and PIN interface |
| V2-B | Transaction preparation and review |
| V2-C | Sepolia EIP-1559 execution |
| V2-D | EIP-7702 delegation and preparation |
| V2-E | Live UserOperation execution |
| V2-F | Recovery and reliability |

Keep changes reviewable and avoid disrupting
existing upstream V1 pull requests.

---

## 9. Testing Strategy

### Automated tests

- Preserve the full V1 regression suite.
- Mock Ethereum RPC and bundler behavior.
- Test chain and signer mismatches.
- Test transaction mutation rejection.
- Test invalid delegation targets.
- Test gas, fee, and nonce boundaries.
- Test submission and receipt failures.
- Test cancellation and recovery.
- Run TypeScript typecheck and production build.

### Physical hardware

- Retail Keycard and OMNIKEY reader.
- PIN lifecycle and device-session verification.
- EIP-1559 and UserOperation signatures.
- Device removal and error behavior.
- Ethereum address recovery.

### Sepolia

- Disposable, minimally funded test account.
- Document every transaction hash.
- Record UserOperation hashes.
- Record receipts and relevant contract addresses.
- Verify expected resulting on-chain state.
- Never use mainnet funds for acceptance tests.

---

## 10. Definition of Done

V2 is complete when a user can:

1. Connect and authenticate to a physical Keycard.
2. Prepare and review an EIP-1559 transaction.
3. Sign and broadcast it on Sepolia.
4. Verify a successful transaction receipt.
5. Prepare a two-call Simple7702 UserOperation.
6. Validate or explicitly authorize delegation.
7. Sign through the physical Keycard.
8. Submit through a supported ERC-4337 bundler.
9. Verify receipts and resulting on-chain state.
10. Recover operation status after an interruption.

No hardware signing key may be imported into Kohaku CLI.

V1 regression tests must continue passing.

The final research document must distinguish
verified capabilities from remaining risks.

---

## 11. Immediate Next Steps

Begin Iteration 0:

1. Verify upstream contribution status.
2. Verify Keycard Go SDK fix provenance.
3. Record current hardware/software versions.
4. Run the baseline test suite.
5. Review current PIN/device implementation.
6. Finalize the threat model.
7. Establish the V2 implementation branch.

Do not begin online signing before the baseline
and security assumptions are established.

---

## Project Principle

Preserve verified cryptography.

Separate preparation, authorization, signing,
submission, and confirmation.

Validate each security boundary independently.

Deliver focused upstream contributions.

V1 proved hardware-backed signing.

V2 will prove controlled hardware-backed execution.
