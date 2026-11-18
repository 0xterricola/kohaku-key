# Reproducing Kohaku Key Experiments

<!-- kohaku-historical-context -->
> **Historical context:** Historical reproducibility notes may describe earlier V1/V2 experiments; consult [current project status](PROJECT-STATUS.md) for the validated final V2 checkpoint and [V3 proposal](V3-PROPOSAL.md) for new experiments.

Updated: November 2, 2026

## Repositories

Research:
https://github.com/0xterricola/kohaku-key

Kohaku CLI integration:
https://github.com/kassandraoftroy/kohaku-cli/pull/68

Offline UserOperation integration:
https://github.com/kassandraoftroy/kohaku-cli/pull/69

Keycard Go fix:
https://github.com/keycard-tech/keycard-go/pull/20

## Local prerequisites

The experiments used:

- A retail Keycard 3.1 and PC/SC reader
- A Keycard CLI binary built with the SDK bug fix
- Node.js 22
- viem 2.55.19

The research build is stored at:

    ~/Developer/kohaku-key/.local/bin/keycard

The `.local` directory is ignored by Git and is not
part of the published research repository.

## Hardware tests

Run with the physical Keycard inserted.

Set `KOHAKU_KEYCARD_CLI` to the patched Keycard CLI path
and supply `KEYCARD_PIN` only for the test process.

From the research repository:

    npm run test:hardware
    npm run test:typed-data
    npm run test:transaction
    npm run test:authorization
    npm run test:user-operation

All tests sign offline data.

The UserOperation test uses a local mock transport that
rejects actual RPC requests.

## Kohaku CLI integration

The TypeScript adapter resides at:

    src/utils/keycard-account.ts

The hardware verification script resides at:

    scripts/verify-keycard-hardware.mjs

Offline EIP-1559 command:

    transact-raw --signer keycard

Offline two-or-more-call Simple7702 mode:

    transact-raw --signer keycard --keycard-userop

The UserOperation command requires explicit nonce,
call gas, verification gas, pre-verification gas, and
fee parameters. Development chain 31337 only.

The tested CLI invocation uses:

    --targets ADDRESS,ADDRESS
    --payloads 0x,0x
    --values 0,0
    --chain-id 31337
    --nonce 0
    --call-gas-limit 100000
    --verification-gas-limit 200000
    --pre-verification-gas 40000
    --max-fee-per-gas 1000000000
    --max-priority-fee-per-gas 100000000

Supply the Keycard binary with `--keycard-cli` or
`KOHAKU_KEYCARD_CLI`. The prototype supplies its
PIN through `KEYCARD_PIN` for the test process.

From the Kohaku CLI repository:

    npm test
    npm run typecheck
    npm run build

November 2 validation: 538/538 tests passed, including
JavaScript regression tests. The physical two-call CLI
UserOperation test produced a valid signature without
RPC requests or bundler submission.

For offline signing, all gas and nonce values are
caller-provided fixtures, not network estimates.

## Version and release caveat

Keycard Go #20 has a fix commit (`c4cf5cc`), but
upstream branch inclusion needs independent re-verification.
A release of Keycard CLI incorporating the fixed SDK
must also be verified separately. The experiments used a
locally compiled version with the corrected SDK.

Do not assume previously installed Keycard CLI binaries
include the fix.
