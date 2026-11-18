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

## R5-B3B — Real SDK state recovery

Test: `tests/v3-r5b-sdk-recovery.sh`

Uses the actual PrivacyPoolsV1Protocol implementation
from @kohaku-eth/privacy-pools 0.1.0-alpha.36.

Verified:
- SDK sync() ingests synthetic pool and entrypoint events.
- Two contiguous owned deposit indexes are discovered.
- Two partial withdrawals are reconstructed.
- Deposit 0 balance: 1000 - 200 - 300 = 500.
- Deposit 1 balance: 600.
- Total recovered balance: 1100.
- Unrelated deposits and withdrawals are excluded.
- history() returns four owned events.
- A fresh SDK instance reconstructs the same balances.

Required event relationship:
PoolDeposited and EntrypointDeposited must reference
the matching commitment. Pool registration supplies
the asset association.

Limitations:
- Events and contract state are synthetic.
- Commitments and labels are placeholder values.
- No proof of cryptographic commitment correctness.
- No physical Keycard used in this test.
- No live-chain state recovery or transactions.
- The SDK currently stops sequential deposit discovery
  at the first missing deposit index.
- Full chain coverage and root verification are not
  established by this integration test.
- Runtime-generated derivation material is not persisted.

Next:
Validate real Privacy Pools cryptographic commitment
construction and replacement-note lineage.
