# Historical Keycard ECDSA determinism experiment

Original experiment recorded November 1, 2026. Preserved from commit `4ca38f9`.

This finding applies only to the specified hardware, applet, and signing workflow.

## Experiment 001 — Retail Keycard ECDSA Determinism

- Date: 2026-11-01
- Hardware: Retail Keycard via HID OMNIKEY 3x21
- Applet: 3.1
- CLI: 4.0.0
- Derivation path: m/44'/60'/0'/0/0
- Input: Identical SHA-256 digest, signed twice
- Signature r: Different
- Signature s: Different
- Recovery v: Different
- Result: NOT DETERMINISTIC

### Conclusion

The tested Keycard APDU ECDSA signing workflow cannot
reliably regenerate identical signature-derived secrets.

Do not use this workflow for Privacy Pools credential
recovery without an alternative, validated mechanism.

### Limitations

- Raw digest signing, not an EIP-712 integration test
- Keycard Shell not tested
- Other applet versions not tested
- Ethereum transaction signing remains viable

### Next steps

1. Continue viem hardware signer integration.
2. Investigate alternative recoverable credential mechanisms.
3. Test Shell independently.
4. Keep privacy credential recovery conditional.
