# Historical PACE benchmark scripts

These scripts were preserved from research commit `e32d940`
for reproducibility and complete research history.

They are not the authoritative benchmark implementation.

The historical `pace_runner.py` appends an additional `0x41`
byte to fixture APDUs. Its exact APDU construction must be
reviewed against the installed research applet before use.

The historical `reconcile_trace.py` does not enforce the full
success conditions required by M3.7, including exact APDU
equality and successful status words.

For current verification, use:

- `RAILGUN/scripts/physical_pace.py`
- `RAILGUN/scripts/reconcile_trace.py`
- `RAILGUN/tests/`

These scripts preserve historical research; their presence
does not establish a production-ready hardware signer.
