# Privacy Pools V1 — Keycard Research

## Scope

Hardware-assisted Privacy Pools V1 credential derivation,
transaction authorization, note recovery, and Keycard Shell
integration.

## Research progression

**V1:** Physical Keycard Ethereum signing and viem integration.

**V2:** Sepolia transaction execution and ERC-4337/EIP-7702
hardware authorization.

**V3:** Keycard 4.x BIP-85-based deterministic Privacy Pools
credentials, deposit/withdrawal flows, and recovery testing.

**V4:** Keycard Shell encrypted QR credential bridge and
experimental Sepolia integration.

## Demonstrated boundaries

The research demonstrated hardware-backed authorization and
reproducible privacy credentials within the respective test
scopes.

Private credential material reached host memory for witness
construction and Groth16 proving. These experiments do not
establish hardware-isolated privacy proving, unlinkability,
or a production-secure privacy wallet.

## Contents

- `docs/`: snapshots of relevant existing documentation
- `scripts/`: snapshots of relevant existing scripts
- `src/`: existing research source snapshots
- `tests/`: relevant test snapshots
- `experiments/`: earlier experimental work
- `applets/`: applet and Shell integration references
- `evidence/`: published result summaries

Legacy snapshots retain their original paths and may require
the original repository structure to execute.
