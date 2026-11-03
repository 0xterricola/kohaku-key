# V3-R2 — Applet 4.0 Hardware Evidence

Status: Physical hardware checkpoint passed.

## Hardware

- Experimental Phonon DAO Keycard
- Applet version: 4.0
- Reader: HID Global OMNIKEY 3x21
- Certificate: Verified against Keycard test CA
- Authentication: Interactive PIN

## Physical results

Two independently authenticated sessions completed.

- Same authenticated card: PASS
- BIP-85 reproducibility: PASS
- BIP-85 index separation: PASS
- ECDH reproducibility: PASS
- ECDH peer separation: PASS

## Security boundaries

BIP-85 entropy and ECDH outputs were processed
only in application memory.

No private keys, entropy, shared secrets, or PINs
were intentionally printed or persisted.

The probe attempts buffer cleanup, but Go does
not guarantee complete memory erasure.

The ECDH peers were the public points G and 2G.
Their known discrete logarithms mean these
particular shared values are not confidential.
This validates ECDH behavior, not secret
credential generation.

No Privacy Pools integration, note recovery,
or hardware-isolated credential security
has been demonstrated.

## Next research

- Design domain-separated ECDH peer derivation
  without publicly known discrete logarithms.
- Test deterministic BIP-85 credential derivation
  using only synthetic software fixtures.
- Define card replacement and backup recovery.
- Compare credential secrecy and recovery properties.
