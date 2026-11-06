# Kohaku Key — Research Findings and Open Questions

**Updated:** November 5, 2026

## Verified findings

1. **V1:** Physical Keycard supports the tested viem-compatible Ethereum signing interfaces.
2. **V1:** Native retail Keycard ECDSA signatures are randomized and cannot be treated as stable note-secret derivation material.
3. **V2:** Physical hardware signing, EIP-7702/ERC-4337 execution, approval controls and Sepolia receipt verification succeeded.
4. **V3 — Privacy Pools V1:** Keycard applet 4.0 supplied reproducible BIP-85-derived credential material across authenticated sessions.
5. **V3:** A real Privacy Pools deposit and hardware-signed partial withdrawal were confirmed on Sepolia.
6. **V3:** Fresh hardware sessions independently recovered the resulting change-note commitment.
7. **V3:** The updated LeanIMT witness passed verification against the pool state.
8. **V3:** A second Groth16 withdrawal proof passed independent verification and two-provider EVM simulation without broadcasting.

The original Keycard Go parser issue was investigated and corrected locally. Official upstream incorporation must be checked independently.

## Credential interoperability

V3 uses a versioned BIP-85/HMAC adapter with the legacy Privacy Pools V1 SecretManager.

The newer signature-derived SignatureSecretManager and legacy HD-derived credentials have different derivation contracts.

V3 results do not establish interchangeable recovery between these schemes.

The tested retail Keycard's randomized ECDSA behavior is incompatible with credential recovery that requires identical canonical ECDSA signature bytes across sessions.

ECDH remains a separate hardware capability and research question. No ECDH-derived Privacy Pools note lifecycle was demonstrated.

## Security findings

The experimental credential root and private witness material entered host memory.

A hardware-held Ethereum signing key does not isolate host-derived privacy credentials.

The demonstrated direct withdrawal exposed public account linkage.

## Not yet established

- Tornado Cash hardware-backed note recovery or execution.
- RAILGUN hardware spending/viewing credential integration.
- Privacy Pools V2 compatibility.
- Replacement-device recovery and arbitrary historical note discovery guarantees.
- Host-compromise resistance or unlinkable direct withdrawal execution.
- Shell-contained credential derivation or Groth16 proving.
- Independent security audit or supported mainnet deployment.

[Project status](PROJECT-STATUS.md) | [V3 report](V3-FINAL-RESEARCH-REPORT.md) | [Hardware compatibility](HARDWARE-COMPATIBILITY.md)
