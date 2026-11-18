# V3-R4 — Cold-Start Privacy Pools Recovery

Status: Physical cold-start recovery checkpoint passed.

## Objective

Verify deterministic Privacy Pools credential
reconstruction across independent application
processes using the same physical Keycard.

## Hardware

- Experimental Phonon DAO Keycard
- Applet 4.0
- Test-CA certificate authentication
- Interactive PIN
- Two independent Go and Node.js process launches

## Experimental derivation contract v1

Hardware source:
- Keycard ExportBIP85
- Path: m/83696968'/128169'/32'/0'
- Output length: 32 bytes
- Card authentication required

Adapter:
- HMAC-SHA256
- HMAC key: runtime-only BIP-85 output
- HMAC input: UTF-8 domain || 0x00 || UTF-8 SDK path
- Domain: kohaku-key/v3-r3/privacy-pools-v1/deriveAt
- Result: 32 bytes encoded as 0x-prefixed hex
- SDK interface: legacy SecretManager deriveAt
- SDK derivation namespace: m/28784'/1'
- Account index: 0

This is a custom experimental derivation adapter.
It is not BIP-32 and is not interchangeable
with the SDK's default keystore.

Do not silently change the BIP-85 path,
HMAC construction, domain, or SDK path mapping
for credentials created under this contract.

## Physical results

- Independent process launch 1: PASS
- Independent process launch 2: PASS
- Deposit precommitment reconstruction: PASS
- Withdrawal precommitment reconstruction: PASS
- Overall cold-start checkpoint: PASS

The test reused the R3 derivation implementation
and compared reconstructed precommitments over
anonymous interprocess pipes.

No actual private keys, derived entropy,
or credential secrets were persisted or logged.

## Limitations

- Recovery uses the same physical card.
- Device-loss recovery remains untested.
- Blockchain note-state rediscovery remains untested.
- Default keystore compatibility is not established.
- Host memory contains sensitive derived material.
- Runtime memory erasure is not guaranteed.
- Test CA is an experimental trust anchor.
- No live Privacy Pools transaction was executed.

## Next milestones

1. Define recovery metadata without storing secrets.
2. Test recovery across supported software versions.
3. Validate backup and replacement-card recovery.
4. Test actual note-state rediscovery.
5. Review credential derivation and memory security.

No production deployment or real funds are authorized
by this proof of concept.
