# V3-R5-D4B — Resumable Sepolia History Scanner

Status: Initial scanner and resume checkpoint verified.

## Contracts

Network: Sepolia (11155111)
Privacy Pools: v1
Initial block: 8587019

## Implementation

tests/v3-r5d4-historical-scan.sh

Default chunk size: 5001 blocks.

Verified:
- Historical public log retrieval
- Contiguous block-range checkpoints
- Atomic checkpoint writes
- Checkpoint integrity validation
- Saved chain-anchor verification
- Recovery after restarting the scanner
- Duplicate and ordering checks
- Finalized-block target selection

## RPC configuration

The ambient SEPOLIA_RPC_URL originally selected
PublicNode, where the scanner's first request failed.

The same range was retrieved using Tenderly.

Validated invocation:

env -u SEPOLIA_RPC_URL R5D4_MAX_CHUNKS=1 \
  tests/v3-r5d4-historical-scan.sh

The scanner defaults to Tenderly when the
environment override is absent.

## Checkpoint storage

~/Library/Application Support/KohakuKeyResearch/
v3-r5d4-sepolia-v1/

Public blockchain events only.

## Limitations

The initial three chunks do not establish full
historical coverage.

Successful responses from one RPC do not
independently prove event completeness.

Cross-provider reconciliation and full finalized
history scanning are remaining research tasks.

No Keycard credentials or secrets are stored.

## Next

Extend finalized history coverage in controlled
batches, verify independent provider consistency,
and integrate public events into SDK recovery.
