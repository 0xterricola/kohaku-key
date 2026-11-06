# Kohaku Key V3 — Final Research Report

**Hardware-backed Privacy Pools V1: deposit, withdrawal, change-note recovery, and subsequent spendability**

| Report metadata | Value |
| --- | --- |
| Status | **Complete — scoped V3 research milestone** |
| Finalized | 2026-11-05 |
| Network | Ethereum Sepolia (`11155111`) |
| Hardware | Physical experimental Keycard, applet 4.0 |
| Protocol tested | Privacy Pools **V1** |
| Implementation | `kohaku-cli`, branch `research/v3-r5e5b9k-deposit-integration` |
| Implementation checkpoint | `9a2a285` — maintainer-facing findings committed locally |
| Report destination | `kohaku-key/docs/V3-FINAL-RESEARCH-REPORT.md` |

> **Disclosure note:** This report deliberately includes public testnet addresses, transaction hashes, and their relationship to a recovered note. Although that information is on-chain, collecting it in one place makes the relationship easier to discover. Review before pushing to a public repository. No PINs, private keys, BIP-85 output, derived credentials, witness inputs, or proofs are included here.

## 1. Executive summary

Kohaku Key V3 completed its **Keycard 4.0 + Privacy Pools V1 research milestone on Sepolia**. The work verified a complete note lifecycle rather than an isolated signing or deposit demonstration:

1. Derive reproducible Privacy Pools credentials from a physical Keycard.
2. Deposit **0.002 ETH** on Sepolia, creating a **0.00198 ETH** note after the protocol's 1% vetting fee.
3. Recover the note from authenticated hardware sessions and generate a verified Groth16 withdrawal proof.
4. Sign and broadcast an explicitly approved **0.00099 ETH** partial withdrawal with the Keycard.
5. Reconstruct the resulting **0.00099 ETH change note** from fresh Keycard sessions and match its commitment to the mined event.
6. Rebuild the post-withdrawal LeanIMT, prove the recovered note's inclusion, and generate a second verified Groth16 withdrawal proof.
7. Successfully simulate that second withdrawal against the pool using **two Sepolia RPC endpoints**, without signing or broadcasting another transaction.

**Principal result:** A Keycard-derived credential can survive an on-chain Privacy Pools V1 withdrawal, be recovered in a new authenticated session, and authorize another valid withdrawal proof. The second spendability test was a contract simulation, **not** a second on-chain spend.

The result establishes **recoverability, cryptographic correctness, and V1 contract interoperability** within the tested setup. It does **not** establish host-compromise resistance, unlinkable withdrawals, Privacy Pools V2 compatibility, or hardware-contained ZK proving.

## 2. Scope and completion criteria

| Research objective | Evidence | Result |
| --- | --- | --- |
| Reproduce credential material across fresh authenticated Keycard sessions | V3-R3; K38-B | **Passed** |
| Deposit a hardware-derived note on Sepolia | K32 receipt and deposit event | **Mined** |
| Produce and independently verify a withdrawal proof | K35-G; K36 | **Passed** |
| Sign an Ethereum withdrawal with the physical Keycard | K37-C; K37-D | **Passed** |
| Execute a partial withdrawal and verify the mined event | K37-D | **Mined** |
| Recover the resulting change note from fresh hardware sessions | K38-B | **Passed** |
| Reconstruct the updated LeanIMT and change-note witness | K39-B | **Passed** |
| Prove the recovered note can authorize another withdrawal | K39-C proof + two `eth_call` results | **Passed in simulation** |
| Execute a second withdrawal on-chain | Not required for this milestone | **Not attempted** |
| Privacy Pools V2 / fully device-contained privacy operations | Outside this V3 milestone | **Not demonstrated** |

**Completion decision:** V3 is complete **for the scoped Privacy Pools V1 hardware-integration and recovery research**. Broader V3 ambitions around stronger secret isolation and newer protocol versions remain separate research tracks; they should not be inferred from this closeout.

## 3. System and trust-boundary architecture

### 3.1 Hardware and software components

| Component | Role |
| --- | --- |
| Experimental Keycard, applet 4.0 | Authenticated BIP-85 entropy derivation; physical ECDSA signing |
| Keycard bridge (Go) | Authenticated device sessions and anonymous-pipe transfer to the Node process |
| `createKeycardR3CredentialProvider` | Versioned, domain-separated conversion from Keycard-derived root material to Privacy Pools credentials |
| Privacy Pools V1 SDK / Kohaku CLI | Commitment calculation, withdrawal encoding, proof integration, and transaction review |
| Host-side prover | In-memory witness calculation and Groth16 proof generation using locally pinned artifacts |
| Ethereum Sepolia | State/ASP roots, deposits, withdrawal execution, logs, and receipt verification |

The tested BIP-85 derivation path was:

```text
m/83696968'/128169'/32'/0'
```

The adapter derives credentials from a **versioned HMAC-based contract** with domain separation for chain, entrypoint, account, deposit index, and withdrawal index. It is **not** standard BIP-32 key derivation. Recovery depends on preserving the same device-root access, derivation contract, coordinate mapping, and protocol rules.

### 3.2 What stays on the Keycard—and what does not

The Keycard authenticates access to its derivation capability and signs an EIP-1559 transaction digest only after the interactive authorization flow. For the privacy credential workflow, however, **derived root material crosses from the Keycard into host process memory** through an anonymous pipe. The host then derives Privacy Pools credentials, assembles private circuit inputs, calculates witnesses, and generates Groth16 proofs.

The implementation intentionally avoided placing secret material in files, shell arguments, logs, and Git, and cleared/disposed in-memory credential providers after use. These engineering controls are useful, but **volatile host memory is not a hardware security boundary**. A compromised host, process-memory disclosure, or side channel remains outside the demonstrated guarantees.

### 3.3 Execution controls

For the real withdrawal, the research workflow required separate interactive **`SIGN`** and **`BROADCAST`** approvals. Before submission it checked the signer, chain, nonce, balances, state/ASP roots, gas parameters, and `eth_call` behavior through both configured RPC endpoints. Following submission, it checked the mined receipt and event fields rather than treating broadcast as success.

The two RPC endpoints were:

- `https://ethereum-sepolia-rpc.publicnode.com`
- `https://sepolia.gateway.tenderly.co`

Their agreement is cross-provider evidence, not a claim of independent consensus verification.

## 4. On-chain transaction record

All ETH values in this report are **Sepolia testnet ETH**, not mainnet funds.

### 4.1 K32 — Initial Privacy Pools deposit

| Property | Verified value |
| --- | --- |
| Transaction | [`0x33c357c4b212ac67f2d93c5f4b97563ae50939dd21f6e3ede19b92520d62a22c`](https://sepolia.etherscan.io/tx/0x33c357c4b212ac67f2d93c5f4b97563ae50939dd21f6e3ede19b92520d62a22c) |
| Block | `12071833` |
| Gross deposit | `0.002 ETH` (`2000000000000000 wei`) |
| Net private note | `0.00198 ETH` (`1980000000000000 wei`) |
| Vetting fee | `0.00002 ETH` (1% of the gross deposit; excludes transaction gas) |
| Deposit index | `17` |
| Outcome | Mined; note commitment and account/credential recovery checked |

### 4.2 K37-D — Physical Keycard-signed partial withdrawal

| Property | Verified value |
| --- | --- |
| Transaction | [`0x3e2b488921a19e0bedddb7858d3cea7cb670cbc1239c50987ae9cdc583f82c1d`](https://sepolia.etherscan.io/tx/0x3e2b488921a19e0bedddb7858d3cea7cb670cbc1239c50987ae9cdc583f82c1d) |
| Block | `12072784` |
| Previous note | `0.00198 ETH` |
| Withdrawn | `0.00099 ETH` (`990000000000000 wei`) |
| New change note | `0.00099 ETH` (`990000000000000 wei`) |
| Signer | Physical Keycard; recovered Ethereum signer checked |
| Authorization | Separate `SIGN` and `BROADCAST` approvals |
| Verification | Two-provider receipt agreement; `Withdrawn` event fields matched verified Groth16 public signals |

The pool emitted a `Withdrawn` event containing the withdrawn value, spent nullifier hash, and new commitment. The research implementation verified those against the previously generated proof's mapped public signals.

**Public change-note commitment:**

```text
0x29b2d484e4251b8040e4df8a9f3a71d35fea5008cbd4f970aff2a471e6148a2a
```

### 4.3 Contract addresses and public state

| Contract / state | Value |
| --- | --- |
| Privacy Pools V1 pool | `0x644d5A2554d36e27509254F32ccfeBe8cd58861f` |
| Entrypoint / ASP root source | `0x34A2068192b1297f2a7f85D7D8CdE66F8F0921cB` |
| Keycard signer / depositor account | `0x155a8332A3504D5F532742Ae6531cd0e28035972` |
| Post-withdrawal state root | `21456747409809235877618994284678988524351012416630627424000389143602581130000` |
| ASP root checked at K39 | `423678871338944881203912428613684557904810681635701283724712449114277672740` |

The ASP root remained unchanged during the observed post-withdrawal checks. The second proof reused the original deposit's association label, while proving inclusion of the **new change commitment** in the updated state tree. The evidence supports this specific V1 path; it is not a claim that arbitrary recovered notes are automatically eligible under every ASP policy.

## 5. Cryptographic verification and note recovery

### 5.1 K35-G and K36 — First withdrawal proof

Two authenticated hardware sessions reproduced the relevant credential material. The host generated a Groth16 withdrawal witness and proof using pinned local V1 circuit artifacts. Independent proof verification used an explicit **single-thread BN128 pairing check**. Both providers then accepted the resulting direct-withdrawal calldata through `eth_call`.

The circuit exposes eight ordered public signals:

| Public signal | Meaning |
| --- | --- |
| `newCommitmentHash` | Commitment to the next note |
| `existingNullifierHash` | Nullifier of the spent note |
| `withdrawnValue` | Amount leaving the note |
| `stateRoot` | State-tree root accepted by the circuit |
| `stateTreeDepth` | Padded state-tree depth |
| `ASPRoot` | Association-set root |
| `ASPTreeDepth` | Padded ASP-tree depth |
| `context` | Binds proof to withdrawal execution context |

The original deposit's state witness was appropriate **before** the mined withdrawal. Once the pool inserted the change commitment, that historical witness and root could not be reused for a second spend.

### 5.2 K38-B — Recovering the first change note

K38-B used **fresh authenticated Keycard sessions**, not credentials retained from K37-D. The same versioned derivation coordinates reconstructed credentials for the first change note at `withdrawIndex: 1`.

The note's precommitment, original deposit label, and **`990000000000000 wei`** remaining balance reconstructed the exact commitment emitted in the mined K37-D withdrawal event. Two independently authenticated hardware sessions agreed. This established a reproducible link between hardware credential derivation and the real change note without requiring another transaction.

### 5.3 K39-B — Updated LeanIMT inclusion witness

The original cached state contained 1,480 inserted leaves. The mined withdrawal inserted the change commitment as **event index 1,481**, at **absolute position 1,480** (zero-based).

| State-tree property | Verified value |
| --- | --- |
| Total leaves after withdrawal | `1481` |
| `LeafInserted` event index | `1481` (one-based) |
| Absolute leaf position | `1480` (zero-based) |
| LeanIMT compressed proof index | `31` |
| Unpadded path siblings | `5` |
| Circuit siblings after padding | `32` |
| Reconstructed root | Matched on-chain root |
| Raw inclusion proof | Verified |

**Important implementation detail:** A LeanIMT proof's **compressed index (`31`) is not its leaf position (`1480`)**. The circuit consumes the compressed index with 32 padded siblings. K39-B independently rebuilt the prior tree, appended the mined change leaf, verified the updated root against both RPC endpoints, and confirmed the raw inclusion proof.

### 5.4 K39-C — Second withdrawal: verified and simulated, not spent

K39-C treated the **recovered change note** (`withdrawIndex: 1`) as the existing note and derived a **new change credential** (`withdrawIndex: 2`). It combined that credential pair with K39-B's refreshed state witness and the current ASP witness.

| Property | Verified result |
| --- | --- |
| Existing recovered note | `0.00099 ETH` |
| Proposed withdrawal | `0.000495 ETH` (`495000000000000 wei`) |
| Proposed new change note | `0.000495 ETH` (`495000000000000 wei`) |
| Existing-note credential | `withdrawIndex: 1` |
| New change-note credential | `withdrawIndex: 2` |
| Groth16 proof | Generated and independently verified |
| Public signal / calldata mapping | Verified |
| PublicNode `eth_call` | Accepted |
| Tenderly `eth_call` | Accepted |
| Second transaction signed | **No** |
| Second transaction broadcast | **No** |

This demonstrates **spendability under the simulated V1 pool execution path**. The actual 0.00099 ETH change note remains unspent by K39-C. A simulated second change commitment is **not** another mined leaf or an independently recovered on-chain note.

## 6. Privacy and security findings

### 6.1 What the experiment establishes

- **Reproducible hardware-derived credentials:** Separate authenticated Keycard sessions reconstruct the same tested note ownership and change-note material.
- **Correct proof and contract integration:** Groth16 public signals, local verification, calldata encoding, and pool execution agree for the tested V1 withdrawals.
- **On-chain verification:** The first withdrawal was actually mined, and its event was checked against the proof and transaction records.
- **Recoverability after state transition:** A new authenticated hardware session can rebuild the resulting note and its current Merkle inclusion witness.
- **Layered transaction authorization:** Signature approval and broadcasting were distinct explicit actions in the real withdrawal flow.

### 6.2 What the experiment does not establish

| Boundary / limitation | Consequence |
| --- | --- |
| BIP-85-derived material enters host memory | Device anchoring does not make credential derivation or witness construction host-isolated |
| Groth16 proving runs on the host | No demonstration of in-card, Keycard Shell, or coprocessor-based proving |
| Direct withdrawal used the original depositor as processor | Publicly observable linkage; **not an unlinkability demonstration** |
| Actual Ethereum transaction contains proof calldata | The on-chain proof is public even though the local proof was not retained in an evidence file |
| Recovery relies on the tested derivation contract | No guarantee of compatibility across applet versions, SDK migrations, or different wallet schemes |
| Experimental Keycard applet 4.0 and test-CA workflow | The result must not be generalized to all retail cards or deployed hardware configurations |
| Privacy Pools V1 was the target | No Privacy Pools V2 credential, circuit, or contract compatibility claim |
| No independent security audit | This is experimentally verified research, not an audited security guarantee |

The local checkpoints were designed not to persist private keys, BIP-85 root material, raw credential secrets, private Groth16 witnesses, proofs, signed transactions, or withdrawal calldata as research artifacts. Those controls were exercised in the described runs; they are **not** proof that a compromised host cannot observe secrets.

## 7. Source code and evidence provenance

### 7.1 Implementation checkpoints (`kohaku-cli`)

| Checkpoint | Commit | Demonstrated result |
| --- | --- | --- |
| K35-G | `963791b` | Hardware-recovered credential and independently verified withdrawal proof |
| K36 | `d7b5985` | Direct-withdrawal calldata and two-provider EVM simulation |
| K37-B | `23c88f6` | Reviewed, unsigned EIP-1559 withdrawal prepared |
| K37-C | `db4f995` | Physical Keycard ECDSA signing and signer recovery |
| K37-D | `d55ba26` | Explicitly approved, mined partial withdrawal |
| K38-B | `a88c112` | Fresh hardware change-note recovery |
| K39-B | `9827d64` | Post-withdrawal LeanIMT witness and on-chain root verification |
| K39-C | `a7bea83` | Second hardware-derived withdrawal proof; two-provider simulation |
| K40-C | `9a2a285` | Sanitized maintainer-facing V1 findings document |

The named Git commits refer to **`kohaku-cli`**. This report is intended for the separate **`kohaku-key`** research repository; it does not imply that the CLI branch has been merged, pushed, or released.

### 7.2 Representative implementation files (`kohaku-cli`)

- `src/utils/keycard-r3-credentials.ts` — research credential adapter and coordinate separation.
- `experiments/v3-r5e5b9k35e-state-witness.mjs` — historical on-chain state-tree reconstruction.
- `experiments/v3-r5e5b9k37d-live-withdrawal.mjs` — reviewed signing/broadcast flow and mined-event checks; **do not replay an already completed live withdrawal**.
- `experiments/v3-r5e5b9k38b-change-note-recovery.mjs` — fresh authenticated hardware recovery.
- `experiments/v3-r5e5b9k39b-change-state-witness.mjs` — updated LeanIMT inclusion proof.
- `experiments/v3-r5e5b9k39c-change-withdraw-simulation.mjs` — subsequent withdrawal proof and read-only `eth_call` simulation.
- `docs/research/KEYCARD-PRIVACY-POOLS-V1-FINDINGS.md` — shorter maintainer-facing account without linked transaction identifiers.

### 7.3 Local evidence inventory (not committed)

The corresponding public-only milestone records and internal audit live outside the source repositories, in the local `KohakuKeyResearch` working directory:

| Evidence record | Role |
| --- | --- |
| `r5-e5b9k32-publicnode-broadcast.json` | Initial mined deposit |
| `r5-e5b9k35g-proof-verification.json` | First Groth16 proof verification |
| `r5-e5b9k36-simulation.json` | First withdrawal `eth_call` checks |
| `r5-e5b9k37d-withdrawal-confirmed.json` | Mined withdrawal evidence |
| `r5-e5b9k37d-submission-journal.json` | Irreversible submission/confirmation journal |
| `r5-e5b9k38b-change-recovery.json` | Two-session recovered change commitment |
| `r5-e5b9k39b-change-state-witness.json` | Updated LeanIMT witness, root, and public siblings |
| `r5-e5b9k39c-change-withdraw-simulation.json` | Subsequent proof and simulation results |
| `K40-INTERNAL-EVIDENCE-REVIEW.md` | Internal cross-milestone review |
| `K40-EVIDENCE-MANIFEST.json` | SHA-256 fingerprints and checkpoint inventory |

K40-A checked consistency across these records and generated an internal review and source fingerprint manifest. The report does not reproduce private working-directory paths or credential-bearing data.

## 8. Engineering lessons

**Proof correctness is not the same as current spendability.** The first note's pre-withdrawal Merkle witness became stale after the new leaf was inserted. Rebuilding the state tree and checking the latest on-chain root were required for K39-C.

**LeanIMT positions and circuit paths are different quantities.** Using the one-based event index or zero-based leaf position in place of the compressed index would corrupt the proof inputs. The tested change note required compressed index `31`.

**Hardware recovery needs stable domain separation.** The exact version and coordinates—chain, entrypoint, account, deposit, and withdrawal index—are part of the recovery contract. Any future mapping or migration must be explicit and independently tested.

**Receipt agreement is stronger than a successful broadcast call.** K37-D confirmed the mined receipt and matched event fields against verified public signals. The actual transaction was the evidence, not merely a returned transaction hash.

**Separate signing and broadcast decisions matter.** K37-D required two explicit approvals; K39-C required neither because its goal was proof verification and simulated execution only.

**Keep the device/host security boundary accurate.** Keycard anchors the credential source and signs transaction digests; the host still sees derived material and generates the ZK proof. Neither an HMAC adapter nor an anonymous pipe alone removes that exposure.

## 9. Follow-on research (not part of V3 completion)

1. **Privacy Pools V2 compatibility:** Compare V2's Rust/SDK interfaces, note model, nullifier and commitment semantics, Merkle/ASP proofs, and transaction APIs with this validated V1 reference.
2. **Versioned credential identifiers and migration:** Specify stable recovery identifiers, hardware/account/chain separation, and deliberate migration behavior without silently changing the established tested derivation contract.
3. **Reduced host secret exposure:** Evaluate a Keycard Shell-contained derivation path and, if feasible, a dedicated trusted coprocessor for credential operations and witness-related work.
4. **Privacy-preserving execution:** Evaluate unlinkable withdrawal and transaction-relaying flows separately from the direct-withdrawal interoperability proof.
5. **Security review and hardware coverage:** Threat-model the host and transport, validate error paths, and test supported applet versions and devices independently.

## 10. Final conclusion

**Kohaku Key V3 is complete within its defined Keycard-backed Privacy Pools V1 Sepolia research scope.**

A real deposit and partial withdrawal were mined. Physical hardware signing was verified. The resulting change note was independently recovered from fresh authenticated Keycard sessions, located in an updated on-chain LeanIMT, and used to produce another verified Groth16 withdrawal accepted by two independent RPC endpoints in simulation.

The demonstrated lifecycle is:

```text
Keycard-derived credentials
    → Sepolia deposit (mined)
    → Groth16 withdrawal proof (verified)
    → Keycard-signed partial withdrawal (mined)
    → Fresh Keycard change-note recovery (verified)
    → Updated LeanIMT inclusion witness (verified)
    → Second Groth16 withdrawal proof (verified)
    → Two-provider contract simulation (accepted; not broadcast)
```

This closes the experimental V1 lifecycle with an auditable reference for future Kohaku and Privacy Pools hardware integrations. **It does not close the separate problems of V2 interoperability, transaction unlinkability, or keeping all privacy secrets inside a trusted device.**
