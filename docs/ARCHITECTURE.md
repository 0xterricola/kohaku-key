# Kohaku Key — Architecture and Trust Boundaries

**Status:** V1/V2 verified PoC; V3 cryptographic and protocol interfaces under investigation.

## Existing Ethereum execution path (V2)

```text
Human transaction intent
  -> Kohaku CLI review, chain/fee/nonce/delegation verification
  -> viem-compatible Keycard LocalAccount
  -> native Keycard bridge -> card-held Ethereum signing key
  -> recover and verify signer / bind approved payload
  -> ERC-4337 bundler / Ethereum RPC
  -> Ethereum receipt and EntryPoint event checks
  -> durable journal + on-chain reconciliation
```

V2 proves one real two-call Sepolia execution. The `kohaku-cli` fork owns this implementation. The original V2 release tag is immutable in this research process.

## Proposed privacy-credential path (V3)

```text
Privacy Pools note/credential specification
  -> audit EnvelopeSigner / wallet recovery contract
  -> capability-tested hardware derivation or ECDH candidate
  -> deterministic, domain-separated test vectors
  -> restart / backup / replacement recovery checks
  -> explicit host/prover data-flow analysis
  -> only then: a protocol-compatible adapter / testnet flow

RAILGUN protocol analysis is separate: do not reuse a credential
scheme without validating spending/viewing/proving requirements.
```

## Distinct secrets

| Material | Where the project is today | V3 question |
| --- | --- | --- |
| Ethereum account signing key | Keycard-held during verified V2 signing | Can continue as authorization backend |
| Privacy Pools credential / note secrets | No hardware isolation or recovery demonstrated | Can a supported primitive reproduce required protocol material safely? |
| RAILGUN spending/viewing material | No hardware implementation demonstrated | Are key requirements compatible with device primitives? |
| ZK proof witnesses / inputs | Host/prover isolation is **not** established | What leaves the device and who can observe it? |

Keycard Shell QR and trusted-display claims require separate validation. Avoid inventing a new universal privacy keystore or altering upstream protocol contracts before compatibility tests.
