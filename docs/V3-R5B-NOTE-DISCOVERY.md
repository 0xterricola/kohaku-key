# V3-R5-B — Offline Privacy Pools Note Discovery

Status: Synthetic event-discovery checkpoint passed.

## SDK

- Package: @kohaku-eth/privacy-pools
- Version: 0.1.0-alpha.36
- Secret manager: legacy SecretManager
- Derivation adapter: V3-R3 experimental contract

## R5-B1 results

- Owned deposits rediscovered
- Unrelated deposits excluded
- Withdrawal nullifier matching
- Noncontiguous deposit indexes supported
- Shortened scan excludes earlier deposits
- Chain-separated decoys excluded

Six checks passed.

The B1 scanner did not independently prove complete
blockchain coverage.

## R5-B2 results

- Distinct withdrawal-chain nullifiers
- Two successive withdrawals reconstructed
- Untouched deposit preserved
- Unrelated events excluded
- Deposit-index gaps handled
- Declared scan-coverage gaps rejected
- Missing initial coverage rejected
- Incomplete chain-tip coverage rejected
- Duplicate nullifier spends rejected
- Exhausted withdrawal search rejected

Ten checks passed.

## Security boundaries

Synthetic derivation roots were generated in memory.

No real Keycard private keys, BIP-85 entropy, PINs,
or credential secrets were persisted.

No physical card access or blockchain transactions
were performed.

## Limitations

The event provider and scan coverage were simulated.

The tests do not yet verify:
- Actual SDK state synchronization
- Replacement-note commitment validation
- Partial-withdrawal remaining balances
- SDK notes() and history() outputs
- Real blockchain state rediscovery
- Recovery after physical card loss

## Next checkpoint

R5-B3: Exercise the SDK's actual synchronization
and note/history reconstruction against an isolated
synthetic event provider.

Preserve the frozen V2 implementation.
