# Kohaku Key — Hardware Compatibility and Research Targets

**Updated:** November 5, 2026

| Hardware | Verified functionality | Not established |
| --- | --- | --- |
| Retail Keycard, applet 3.1 (OMNIKEY reader) | Viem-compatible EIP-191/EIP-712/EIP-1559/EIP-7702 signing; ERC-4337 execution; EIP-1581 public derivation across reconnects; randomized native ECDSA | Reproducible signature-derived privacy credentials, independent trusted hardware display |
| Experimental Phonon DAO card, Keycard applet 4.0 | Authenticated BIP-85 derivation, reproducible Privacy Pools V1 credentials, deposit, withdrawal signing and change-note recovery | Shell-contained credentials, general V2 protocol compatibility |
| Keycard Shell | Existing hardware and custom-firmware research target | Kohaku-specific derivation, witness isolation, native ZK proving |
| YubiKey / other devices | No Kohaku Key integration demonstrated | Credential compatibility, recovery and ZK capabilities |

## Verified evidence

- [V1 outcome](V1-OUTCOME.md)
- [V2 Sepolia results](V2-TESTNET-RESULTS.md)
- [V3 Privacy Pools V1 report](V3-FINAL-RESEARCH-REPORT.md)
- [V3 applet 4.0 evidence](V3-R2-APPLET4-HARDWARE-EVIDENCE.md)
- [V4 Shell architecture](V4-KEYCARD-SHELL-ARCHITECTURE-DRAFT.md)

## Hardware derivation and capability boundaries

The tested V2 Ethereum account path was `m/44'/60'/0'/0/0`.

Applet 3.1 EIP-1581 public derivation was tested separately from private credential export and recovery. Public derivation does not establish safe private-key export.

Applet 4.0 exposes BIP-85 and ECDH capabilities. The completed V3 integration uses BIP-85; it does not demonstrate an ECDH-derived privacy protocol.

## Cryptographic distinctions

The retail Keycard's native ECDSA signatures were observed to be randomized. Valid signatures do not necessarily reproduce identical signature bytes.

V3 used an experimental Keycard 4.0 BIP-85/HMAC credential contract, not deterministic ECDSA signature bytes.

The V3 root entered host memory. This is distinct from keeping all privacy credentials inside a secure element.

Do not mix derivation schemes or silently change existing recovery paths and indexes.

Hardware tests must identify actual applet capabilities, transports, derivation coordinates, recovery behavior and secret-exposure boundaries without recording secret material.
