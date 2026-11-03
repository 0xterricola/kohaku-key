# Kohaku Key — Research Findings and Open Questions

**Last consolidated:** November 2, 2026. These statements distinguish validated evidence from proposed experiments.

## Verified

1. A physical Keycard can supply valid Ethereum signatures through a viem-compatible account without exporting its private key (V1).
2. EIP-7702 and two-call ERC-4337 authorization and execution were demonstrated with physical hardware and independently verified on Sepolia (V2).
3. Native Keycard ECDSA uses randomized signing nonces. Its signatures do **not** provide the reproducible byte stream needed by a naïve signature-derived privacy credential scheme (V1).
4. A legacy Keycard Go ECDSA parser issue affected initial recovery experiments; corrected signing/recovery behavior was tested locally. Current official SDK incorporation must be verified separately.
5. Host review controls do not create an independently trusted hardware display. Card-held Ethereum keys do not mean host-side privacy secrets remain isolated.

## Not yet established

- Whether Keycard applet 3.1 exposes a usable and safely scoped BIP-85 mechanism for Privacy Pools credential construction.
- Whether the experimental applet 4.0 card exposes ECDH with repeatable and appropriately isolated key agreement semantics.
- Whether outputs from either primitive match Privacy Pools `EnvelopeSigner` and note recovery requirements.
- Whether backup/replacement reproduces the same credential without risky host exposure.
- Whether RAILGUN's actual spending, viewing and proof requirements admit a useful hardware boundary.

## Decision rule

No funded privacy-note experiment before successful deterministic vectors, restart and backup recovery, and protocol-compatibility checks. A negative finding is useful; document the unsupported boundary instead of changing cryptographic assumptions to fit a narrative.

See [V3 proposal](V3-PROPOSAL.md), [hardware matrix](HARDWARE-COMPATIBILITY.md), and [V1 outcome](V1-OUTCOME.md).
