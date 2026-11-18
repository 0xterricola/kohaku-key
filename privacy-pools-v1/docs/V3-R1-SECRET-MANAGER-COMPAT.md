# V3-R1 — Privacy Pools Secret Manager Compatibility

**Status:** Offline software compatibility verified.
**SDK:** @kohaku-eth/privacy-pools 0.1.0-alpha.36
**Result:** Seven compatibility checks passed.

## Objective

Determine whether Privacy Pools' legacy ISecretManager
can consume an external deterministic derivation provider.

## Method

A simulated derivation provider generates runtime-only
test material using random roots and HMAC-SHA256.

No physical Keycard private keys are accessed.
No cryptographic test secrets are persisted or logged.

This simulation is not a BIP-32 implementation.

## Verified

- Deterministic deposit reconstruction
- Initial note compatibility
- Partial-withdrawal reconstruction
- Deposit-index separation
- Chain separation
- Root-key separation
- Ephemeral signer reproducibility

The separate R0 regression suite also passed eight checks.

## Security boundaries

The test demonstrates compatibility with the SDK's
derivation interface, not compatibility with actual
EIP-1581 key derivation.

It does not establish:

- Hardware-isolated privacy credentials
- Physical private-key derivation or export
- Device-loss or backup recovery
- Real blockchain-state note rediscovery
- Production cryptographic security

## Next investigation

Assess whether applet 3.1 EIP-1581 can provide a
meaningful hardware security boundary without exporting
real private material into application storage.

Compare this with applet 4.0 BIP-85 and ECDH.

Do not export or persist real private keys for this study.
