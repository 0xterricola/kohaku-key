# Kohaku Key — V2 Testnet Results

**Status:** Not started
**Network:** Ethereum Sepolia
**Chain ID:** 11155111

This document records independently verified
testnet execution evidence.

No live V2 transaction or UserOperation has
been completed as of this initial document.

## Environment

- Execution date:
- Kohaku CLI commit:
- Keycard SDK revision:
- Keycard CLI revision:
- Hardware:
- RPC provider:
- Bundler provider:
- EntryPoint address:
- Simple7702 implementation:
- Verified implementation code hash:

## Experiment 1 — EIP-1559

- Status: Not started
- Transaction intent:
- Sender:
- Recipient:
- Value:
- Nonce:
- Gas and fees:
- Signed transaction hash:
- Broadcast transaction hash:
- Receipt block:
- Receipt status:
- Confirmations:
- Recovered signer:
- Expected state:
- Observed state:

### Validation

- [ ] Chain verified.
- [ ] Intent reviewed.
- [ ] Keycard signature verified.
- [ ] Transaction broadcast.
- [ ] Receipt confirmed.
- [ ] Expected on-chain state verified.
- [ ] No software signing key used.

## Experiment 2 — Simple7702 UserOperation

- Status: Not started
- Account:
- Delegate implementation:
- Delegation code hash:
- Existing delegation state:
- Authorization required:
- EntryPoint:
- EntryPoint nonce:
- Call 1:
- Call 2:
- Prepared UserOperation hash:
- Submitted UserOperation hash:
- Resulting transaction hash:
- Receipt block:
- Execution status:
- Expected state:
- Observed state:

### Validation

- [ ] Delegation state verified.
- [ ] Implementation trusted.
- [ ] All calls reviewed.
- [ ] Keycard signature verified.
- [ ] Bundler submission accepted.
- [ ] UserOperation receipt verified.
- [ ] Ethereum transaction receipt verified.
- [ ] Expected on-chain state verified.
- [ ] No software signing key used.

## Failure and Recovery Experiments

| Scenario | Expected behavior | Result |
|---|---|---|
| Reader disconnect | Signing fails safely | Pending |
| Incorrect PIN | Explicit failure | Pending |
| Chain mismatch | Signing blocked | Pending |
| Invalid delegation | Authorization blocked | Pending |
| Stale nonce | Reprepare required | Pending |
| RPC timeout | Reconcile state | Pending |
| Bundler timeout | Reconcile operation | Pending |
| Execution revert | Report failure | Pending |
| CLI restart | Resume monitoring | Pending |

## Evidence and References

Add transaction explorer URLs, receipts,
test logs, and implementation commit references.

Never store PINs, mnemonic phrases, private
keys, or other recovery secrets.

## Final Verification

Not completed.
