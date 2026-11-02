# Reproducing Kohaku Key Experiments

Updated: November 2, 2026

## Repositories

Research:
https://github.com/0xterricola/kohaku-key

Kohaku CLI integration:
https://github.com/kassandraoftroy/kohaku-cli/pull/68

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

The offline command is:

    transact-raw --signer keycard

The CLI currently requires explicit transaction
parameters, limits signing to development chain 31337,
and disables broadcasting.

## Version and release caveat

Keycard Go #20 was merged into upstream develop.

A release of Keycard CLI incorporating the fixed SDK
must be verified separately. The experiments used a
locally compiled version with the corrected SDK.

Do not assume previously installed Keycard CLI binaries
include the fix.
