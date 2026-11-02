# Research Findings

## Known architecture
- Public transaction paths currently use software keys.
- viem supports custom LocalAccount implementations.
- Privacy Pools provides an EnvelopeSigner interface.
- Other privacy plugins use the Keystore contract.

## Open questions
1. Does Keycard reproduce canonical signature components?
2. Does Shell produce compatible signatures?
3. Can credentials be recovered across devices and backups?
4. What are the exact hardware approval guarantees?
5. Which upstream transaction call sites need refactoring?

Record tested firmware versions, commits, evidence, and results.
Do not treat assumptions as completed tests.

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
