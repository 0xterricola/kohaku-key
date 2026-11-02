# Experiment 002 — Retail Keycard ECDSA Signing

## Hardware
- Retail Keycard, applet 3.1
- HID Global OMNIKEY 3x21
- Derivation path: m/44'/60'/0'/0/0
- Address: 0xB8A0f79E6d64c948E9F5ea32aD93647777915EBa

## Discovery
keycard-go v4.0.2 corrupts legacy ECDSA signature
components during recovery-ID calculation.

In types/signature.go, calculateV contains:

    rs := append(r, s...)

The r and s slices share a DER response buffer.
Appending to r can overwrite the memory backing s.

## Verified fix

    rs := append(append([]byte{}, r...), s...)

An isolated build of keycard-cli using this fix produced:

- ECDSA verification: VALID
- Exported and recovered Ethereum addresses: MATCH
- Private key remained on the hardware card
- No transaction was broadcast

## Next steps
- Add an SDK regression test and submit upstream fix
- Verify corrected EIP-191 message signing
- Retest signature determinism using valid signatures
- Implement a viem-compatible Keycard account adapter

## Scope
Results apply to the tested retail Keycard 3.1 and
keycard-go v4.0.2. Keycard Shell and applet 4.0
have not been validated in this experiment.

<!-- research-update:start -->
## Research update — November 2, 2026

See [Project Status](PROJECT-STATUS.md) and
[Security and Recovery Findings](SECURITY-AND-RECOVERY.md)
for validated hardware signing, upstream SDK fix status,
signature determinism findings, and current limitations.

Keycard Go #20 has merged upstream. EIP-191, EIP-712,
EIP-1559, EIP-7702 authorization, and offline Simple7702
UserOperation signing have been verified on retail Keycard
3.1. Signature-derived credential recovery is not
supported by the card's randomized ECDSA signing mode.
<!-- research-update:end -->
