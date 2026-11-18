# Physical JavaCard benchmark runner

Status: **hardware preflight implemented; physical ECC/PACE benchmark
replay not yet implemented**.

## Requirements

A dedicated test card with an already-installed compatible research
applet, a PC/SC reader, Python 3, and pyscard.

JCOP3 binaries are supplied for research comparison, but compatibility
with JCOP4 and JCOP4.5 has not been established.

## Setup

From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install pyscard
python3 -B RAILGUN/scripts/benchmark.py
python3 -B RAILGUN/scripts/hardware_preflight.py --list-readers
```

To check an already-installed experimental applet:

```sh
python3 -B RAILGUN/scripts/hardware_preflight.py \
  --reader "EXACT PCSC READER NAME" \
  --applet pace-gm \
  --select-only --confirm-test-card
```

Choose `native-ec` to check the other experimental applet.

The command sends only an ISO 7816 SELECT-by-AID APDU.
It never installs or deletes an applet, authenticates a wallet,
requests a PIN, or executes cryptographic benchmark APDUs.

A missing applet may return `6A82`. SELECT success proves only
that the AID is selectable, not hardware/algorithm compatibility.

## Next research milestone

Publish an explicit opt-in physical benchmark runner using verified
public setup commands and test vectors, with per-card timing reports.
Keep installation instructions separate and require manual review.

Do not install experimental applets on cards holding valuable keys.
Never treat a successful applet SELECT as a verified benchmark.
