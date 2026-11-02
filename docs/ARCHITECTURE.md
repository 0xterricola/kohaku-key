# Architecture

Kohaku CLI
  - Public transactions: viem LocalAccount
  - Privacy Pools: Kohaku EnvelopeSigner
  - Other private protocols: existing software Keystore

Hardware backend
  - Keycard smartcard/APDU interface
  - Keycard Shell transport evaluated separately

Do not invent a replacement keystore for V1.
Do not assume public signing and privacy proving use the same
cryptographic primitives.
