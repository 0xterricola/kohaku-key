# V3-R5-E — Deterministic Credential Identifiers

Status: Required V3 architectural PoC.

## Decision

A reproducible credential identifier maps to an
unambiguous location in the existing deterministic
Privacy Pools credential derivation hierarchy.

Preserve the proven V3-R3 BIP-85 root and HMAC
adapter. Do not silently change derivation paths.

## Identifier v1

Canonical representation:

kkid:v1:privacy-pools-v1:eip155:<chainId>:<entrypoint>:<accountIndex>:<depositIndex>:<role>:<secretIndex>

Roles:
- deposit: secretIndex = 0
- withdraw: secretIndex >= 1

The identifier describes the location of a credential.
It is not itself a secret or cryptographic commitment.

All integers use unpadded decimal representation.
Entrypoint addresses use lowercase 20-byte hex.

## SDK compatibility

Map the identifier to existing SDK coordinates:

- chainId
- entrypointAddress
- accountIndex
- depositIndex
- deposit secret / withdrawal secret index

The existing SDK ppPath implementation defines the
actual hardened path values. Do not invent or modify
its secret-type encoding.

The BIP-85 root extraction and HMAC derivation domain
remain unchanged in V3.

A different derivation algorithm or hierarchy requires
a new explicit derivation-contract version.

## Security

- Never derive credential IDs from secret material.
- Never use a commitment as its own derivation ID.
- Do not publish persistent account identifiers by default.
- Separate networks, protocols and contract contexts.
- Never persist derived credential secrets.
- Public IDs do not guarantee transaction unlinkability.
- Host-memory exposure remains an experimental limitation.

## Recovery

A complete recovery must establish:

1. Same physical card and derivation contract
2. Same identifier and network/Entrypoint context
3. Identical derived credential material
4. Matching Privacy Pools SDK note discovery
5. Correct recovered withdrawal history and balance
6. No credential-secret backup required

Identifier discovery is separate from derivation.
The SDK's sequential-index discovery limitation
must be handled explicitly.

## Scope

V3:
- Privacy Pools identifier contract
- Deterministic mapping regression tests
- Physical Keycard cold-recovery PoC
- Public blockchain history integration

V4 research:
- RAILGUN integration
- Additional protocol-specific namespaces
- General-purpose credential framework

## Sequence

Finish R5-D historical scanning.
Then implement and validate R5-E hardware recovery.

This document records the architectural decision.
It does not claim hardware mapping is implemented.
