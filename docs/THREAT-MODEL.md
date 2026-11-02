# Threat Model

## In scope
- Extraction of Ethereum signing keys from the host
- Accidental software import of hardware private keys
- Signature determinism and privacy-note recoverability
- Device loss and backup compatibility investigation

## Not protected in V1
- Compromised host constructing malicious signing requests
- Privacy spending secrets present during ZK proof generation
- Secret-deriving signatures copied from host memory
- RPC metadata and network-level correlation

## Approval boundary
A screenless Keycard cannot independently display transaction
details. Keycard Shell has a display, requiring separate validation.

## Recovery boundary
Identical addresses do not establish identical privacy notes.
Signature derivation and recovery compatibility must be tested.
