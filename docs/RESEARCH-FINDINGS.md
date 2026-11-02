# Research Findings

## Known architecture
- Public transaction paths currently use software keys.
- viem supports custom LocalAccount implementations.
- Privacy Pools provides an EnvelopeSigner interface.
- Other privacy plugins use the Keystore contract.

## Open questions
1. Does Keycard reproduce canonical signature components?
2. Does Shell produce compatible signatures?
3. Can credentials be recovered across devices and backups?
4. What are the exact hardware approval guarantees?
5. Which upstream transaction call sites need refactoring?

Record tested firmware versions, commits, evidence, and results.
Do not treat assumptions as completed tests.
