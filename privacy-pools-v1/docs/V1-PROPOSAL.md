# Kohaku Key — V1 Technical Proposal

<!-- kohaku-historical-context -->
> **Historical context:** Historical V1 proposal. The V1 offline prototype is complete; original live Sepolia acceptance was satisfied later in V2. Current results: [V1 outcome](V1-OUTCOME.md), [V2 outcome](V2-OUTCOME.md).

**Hardware-Backed Ethereum Signing & Privacy Credential Research**

- **Status:** Research & Development
- **Date:** November 2026
- **Research:** https://github.com/0xterricola/kohaku-key
- **Upstream:** https://github.com/kassandraoftroy/kohaku-cli

---

## 1. Project Overview

Kohaku Key explores hardware-backed security for Ethereum privacy
wallets, beginning with native Keycard integration for Kohaku CLI.

The objective is to enable Ethereum transactions to be signed using
physical security devices while investigating whether those devices
can support deterministic privacy credential recovery.

V1 reuses existing interfaces from viem, Keycard, and the Kohaku
Privacy Pools SDK rather than introducing new cryptographic protocols.

### V1 Goals

1. Enable hardware-backed Ethereum transaction signing.
2. Integrate Keycard through viem account interfaces.
3. Investigate deterministic hardware-derived privacy credentials.
4. Deliver focused, independently reviewable upstream contributions.

**Long-term vision:** Reusable hardware-backed authorization and
privacy credential recovery for Ethereum wallets.

---

## 2. Proposed Architecture

### Ethereum Signing — viem

Kohaku CLI currently uses software-managed private keys for public
Ethereum account operations.

V1 will refactor relevant transaction paths to accept viem account
objects, allowing software and hardware signers to share execution
infrastructure.

The initial hardware backend will use Keycard's APDU interface.

Keycard Shell QR signing will be evaluated as a separate transport.

### Privacy Credentials — EnvelopeSigner

Kohaku's Privacy Pools integration already provides signature-based
credential derivation through its EnvelopeSigner interface.

V1 will investigate whether Keycard can produce the deterministic
signatures needed for reliable credential reconstruction.

No new credential vault or derivation protocol is planned for V1.

### Architecture

    Kohaku CLI
        |
        +-- Ethereum Execution
        |       |
        |       +-- viem Account
        |               |
        |               +-- Software Signer
        |               |
        |               +-- Keycard Signer
        |
        +-- Privacy Pools
                |
                +-- EnvelopeSigner
                        |
                        +-- Keycard Adapter (conditional)

Hardware-protected Ethereum signing keys do not automatically imply
hardware-isolated privacy spending credentials.

---

## 3. Development Roadmap

### Iteration 0 — Hardware Feasibility

**Objective:** Determine whether Keycard supports reproducible
signature-derived credentials.

Implementation:

- Create canonical EIP-712 test vectors.
- Sign identical envelopes repeatedly.
- Compare full signatures, including r, s, and recovery information.
- Evaluate canonical low-s normalization.
- Repeat across hardware sessions and device restarts.
- Record firmware versions and derivation paths.
- Test standalone Keycard and Keycard Shell independently.
- Verify compatibility with the exact signature bytes or values
  consumed by the Kohaku Privacy Pools SDK.
- Verify credential reconstruction after application restart.

**Deliverable:** Reproducible test harness and compatibility report.

**Decision gate:** Privacy credential integration proceeds only when
deterministic signing and successful recovery are demonstrated.

Identical Ethereum addresses alone do not prove that two devices or
signer implementations derive identical privacy credentials.

### PR #1 — Ethereum Signer Refactor

**Objective:** Make Kohaku CLI hardware-signer compatible.

Implementation:

- Replace raw private-key parameters in public Ethereum transaction
  paths with appropriate viem account abstractions.
- Preserve existing software signing.
- Keep privacy-plugin Keystore.deriveAt APIs unchanged.
- Update EIP-7702 execution call sites as needed.
- Add regression tests and type checks.
- Avoid introducing hardware dependencies into this PR.

**Deliverable:** Focused upstream signer refactor.

**Acceptance criteria:**

- Existing tests pass.
- Existing software-wallet behavior remains unchanged.
- Ethereum execution supports an externally supplied signer.
- No private protocol credential changes are required.

### PR #2 — Native Keycard Signer

**Objective:** Execute Ethereum transactions using Keycard hardware.

Implementation:

- Implement a Keycard-backed viem account.
- Support hardware account discovery.
- Implement APDU-based signing.
- Validate Ethereum transaction signing.
- Validate EIP-712 typed-data signing.
- Evaluate EIP-7702 authorization signing.
- Evaluate Shell QR as an independent transport.
- Add hardware and mocked integration tests.

**Deliverable:** Hardware-signed Sepolia transaction through Kohaku CLI.

**Acceptance criteria:**

- Ethereum signing keys are not imported into host application memory.
- Signatures verify against the expected hardware account.
- Signed transactions are successfully broadcast.
- Device and transport limitations are documented.

### PR #3 — Privacy Pools Integration

**Objective:** Investigate hardware-derived privacy credential recovery.

Implementation:

- Adapt Keycard signing to the existing EnvelopeSigner interface.
- Validate canonical signature determinism.
- Verify exact credential derivation compatibility.
- Test application restart and credential reconstruction.
- Evaluate device replacement and backup limitations.
- Document secret exposure during host-side operations.

**Deliverable:** Demonstrated reproducible privacy credential recovery.

**Acceptance criteria:**

- Deterministic output is confirmed on supported hardware.
- Credential recovery succeeds across application restarts.
- Existing Privacy Pools behavior remains compatible.
- No experimental funds are deposited before recovery is verified.

**Fallback:** If signature determinism or compatibility fails,
defer PR #3. PR #1 and PR #2 remain independently valuable.

---

## 4. Security Model

### Protected in V1

- Ethereum signing keys remain inside Keycard hardware.
- Transactions can be signed without software private-key import.
- Hardware account integration is separated from wallet execution.

### Not Protected in V1

- A compromised host can construct malicious signing requests.
- Screenless devices cannot independently display transaction details.
- Privacy credentials may enter host memory during proof generation.
- Signatures used to derive secrets may themselves be sensitive.
- RPC metadata and transaction timing may expose wallet activity.
- Device loss does not automatically guarantee credential recovery.

### Hardware Approval

Standalone Keycard and Keycard Shell have different approval models.

Keycard Shell's display and QR signing require separate validation.
A hardware signature does not inherently prove informed user approval.

### Recovery Requirements

Recovery tests must verify the exact protocol credential, not merely
matching public addresses.

Repeated signatures, firmware compatibility, derivation paths,
encoding, and device replacement must be evaluated.

Use disposable test credentials throughout development.

---

## 5. V1 Scope

### Included

- Standalone Keycard hardware.
- Keycard Shell compatibility research.
- APDU signing.
- Viem-compatible account integration.
- Ethereum transaction signing.
- EIP-712 deterministic-signature research.
- EIP-7702 compatibility investigation.
- Privacy Pools EnvelopeSigner experiments.
- Automated tests and developer documentation.

### Excluded

- Custom hardware manufacturing.
- YubiKey adapters.
- New privacy vault cryptography.
- Railgun spending-key isolation.
- Casberi NFC integration.
- Hardware-isolated ZK proof generation.

These are possible future projects, not V1 commitments.

---

## 6. Development Strategy

### Research Repository

**0xterricola/kohaku-key**

Contains:

- Architecture and security documentation.
- Hardware compatibility investigations.
- Signing experiments.
- Test vectors.
- Prototype adapters.
- Reproducible research findings.

### Upstream Repository

**kassandraoftroy/kohaku-cli**

Contains:

- Production implementation.
- Integration tests.
- Regression tests.
- Focused upstream pull requests.

Experimental work should be validated independently before being
introduced into Kohaku CLI.

Each upstream PR should remain independently reviewable.

---

## 7. V1 Success Criteria

### Core Success — Required

A user initiates an Ethereum transaction through Kohaku CLI,
authorizes it using Keycard hardware, and broadcasts it on Sepolia.

The hardware Ethereum private signing key is never imported
into Kohaku CLI's application memory.

This is the primary committed V1 milestone.

### Research Success — Conditional

Keycard reliably derives credentials compatible with Kohaku's
Privacy Pools signature-based recovery mechanism.

The resulting credentials can be reconstructed after application
restart using the documented supported hardware configuration.

This remains a research milestone until feasibility is proven.

---

## 8. Future Direction

### V2 — Hardware-Assisted Privacy Recovery

Investigate hardware-gated credential storage, encrypted backups,
device replacement, and recovery strategies.

### V3 — Private Transaction Authorization

Expand hardware-backed authorization into supported privacy
workflows and evaluate Railgun integration.

### Future — Mobile and NFC

Explore integration with Casberi, YubiKey, and other supported
hardware authentication devices.

These projects depend on validated V1 results.

---

## 9. Immediate Work

1. Establish the standalone Keycard test environment.
2. Inspect the existing Keycard signing APIs and firmware behavior.
3. Build canonical EIP-712 test vectors.
4. Implement repeated-signature determinism tests.
5. Record results across sessions.
6. Run equivalent tests against Keycard Shell.
7. Begin the viem signer refactor in Kohaku CLI.

The signature-determinism experiment should happen before any
privacy funds are deposited.

---

## Project Principle

**Reuse existing interfaces. Validate cryptographic assumptions.
Ship focused upstream contributions.**

Kohaku Key starts as a practical hardware-signing integration,
with a longer-term ambition to make Ethereum privacy credentials
more secure and recoverable.

---

*Independent open-source research project. Not an official Kohaku,
Ethereum Foundation, or Keycard product.*

<!-- research-update:start -->
## Research update — November 2, 2026

See [Project Status](PROJECT-STATUS.md) and
[Security and Recovery Findings](SECURITY-AND-RECOVERY.md)
for validated hardware signing, upstream SDK fix status,
signature determinism findings, and current limitations.

Keycard Go #20 fix commit c4cf5cc exists;
the current upstream branch/release status needs re-verification. EIP-191, EIP-712,
EIP-1559, EIP-7702 authorization, and offline Simple7702
UserOperation signing have been verified on retail Keycard
3.1. Signature-derived credential recovery is not
supported by the card's randomized ECDSA signing mode.
<!-- research-update:end -->

## V1 implementation outcome — November 2, 2026

See [V1 Outcome](V1-OUTCOME.md).

Offline Keycard Ethereum signing and the Kohaku CLI integration
were implemented and tested through upstream PRs #67, #68, and
#69. The local milestone passed 538 tests.

The original Sepolia broadcast acceptance criterion was not
performed. Therefore, the offline signing prototype is complete
but the proposal's original end-to-end success criterion remains open.

The signature-derived Privacy Pools recovery path was not
implemented because deterministic credential recovery has
not been established on the tested Keycard signing mode.
