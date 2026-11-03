# Kohaku Key — Hardware Compatibility and Research Targets

**As of:** November 2, 2026. Proven Ethereum signing is distinct from proposed privacy derivation.

| Hardware | Tested functionality | Not yet established |
| --- | --- | --- |
| Retail Keycard, applet 3.1, OMNIKEY reader | EIP-191, EIP-712, EIP-1559, EIP-7702, Simple7702/ERC-4337 signing; V2 Sepolia execution | BIP-85 API capability, deterministic recoverable Privacy Pools note derivation, trusted on-device display |
| Experimental Phonon DAO card, Keycard applet 4.0 | Card available for V3 investigation; not part of the V2 on-chain proof | ECDH API behavior, key lifecycle, output exposure, derivation determinism, recovery and privacy-protocol compatibility |
| Keycard Shell | Separate potential QR / air-gapped signing track | Matching signing semantics and trusted display / private-note credential support |
| YubiKey and other devices | Longer-term candidate only | No V1/V2/V3 integration accepted or demonstrated |

## Evidence and experiments

V2 utilized `m/44'/60'/0'/0/0` on retail Keycard applet 3.1, with native interactive PIN entry and a Go bridge. The independent Sepolia proof and 647-test checkpoint are in [V2 testnet results](V2-TESTNET-RESULTS.md).

V1 established randomized native ECDSA signatures. **Do not feed raw ECDSA signature bytes to a persistent note-secret derivation workflow.** BIP-85 availability on 3.1 and ECDH operations on 4.0 are research questions, not validated capabilities in this project.

Any V3 device experiment must log applet version, derivation path/key selector, supported APDUs, context input, output length, reproducibility, re-pairing behavior, backup limitations and which secrets become visible to the host—without recording the secrets themselves.
