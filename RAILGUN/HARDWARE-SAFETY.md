# RAILGUN physical benchmark safety

## Scope

`RAILGUN/scripts/physical_pace.py` is the primary live
PACE-GM public-vector runner.

The legacy `pace_runner.py` keeps offline replay but its
command-line live mode is disabled.

## APDU restrictions

The primary runner permits only:

- SELECT for the explicitly selected research applet AID
- Read-only stage query `80710000`
- The ten published public PACE-GM vector APDUs

The allowlist is checked before each transmission. The
complete vector set is compared against the published fixture
before SELECT.

The runner does not perform GlobalPlatform authentication,
package loading, applet installation, deletion, PIN handling,
wallet signing, or applet stage initialization.

PACE-GM public-vector execution may still update internal
research-app state. It is not a guarantee of zero card writes.

## Authorization and card identity

Live execution requires `--confirm-test-card` and
`--execute-public-vectors`.

Those flags are explicit operator authorization. They do
NOT authenticate the identity of the inserted card.

SELECT success and stage 11 verify the expected research
applet and its reported initialization stage, not the
absence of a wallet or unrelated installed applets.

The PC/SC reader name identifies a reader, not a unique
physical card.

Use only a separately verified dedicated research card.
Do not use an initialized wallet card.

## Applet selection

- `published`: F0424E3235343C01
- `jcop4-k1`: F0424E3235344E01

These names select an applet configuration; they do not
attest JCOP hardware generation.

## Failure handling

Execution stops on unexpected APDUs, invalid fixtures,
unexpected status words, wrong stage, and incorrect point
outputs. SW `6F02` includes a JCOP4 provider-specific
initialization diagnostic, not a universal diagnosis.

No automated recovery, card provisioning, or retry is
performed.

## Offline validation

Run:

    python3 -B -m unittest discover -s RAILGUN/tests -p test_physical_pace.py -v
    python3 -B RAILGUN/scripts/benchmark.py

These commands do not access a physical card.

Physical behavior of our locally built `4E00/4E01` CAP
remains unverified; Mikkoph's separate JCOP4 `4D00`
variant has independent physical-vector evidence.
