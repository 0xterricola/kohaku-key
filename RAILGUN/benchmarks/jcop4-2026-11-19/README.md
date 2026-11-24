# Original JCOP4 physical benchmark JSON — Nov 19, 2026

Contributor: **Mikkoph (bitgamma), Keycard developer**. Original methodology and report: https://gist.github.com/bitgamma/18bed236b7073b8b951f26ba68e76515 . JSON files were supplied in the Nov 23 research conversation and archived here **byte-for-byte**, without synthesized samples or edits. Import/validation date: Nov 23, 2026. These are independently reported experiments on the developer's JCOP4 setup, *not* runs performed on this repository owner's JCOP3 or future JCOP4 hardware.

| Raw file | SHA-256 | Outcome |
| --- | --- | --- |
| [`JCOP4-algoprobe-2026-11-19.json`](raw/JCOP4-algoprobe-2026-11-19.json) | `2c29c5dc520a8962cb173393319e0f7acd8bb0d249a24fe398e79bb1f772a0b6` | Cofactor/provider algorithm probe; K=1 XY and PACE accepted |
| [`JCOP4-native-ec-2026-11-19.json`](raw/JCOP4-native-ec-2026-11-19.json) | `5ec9f747fbf1a034e20e37543aaa47b192adb43064dba090d6fc87de036c8944` | PARTIAL: 11/18 operation categories verified; original full-XY failed |
| [`JCOP4-pace-gm-2026-11-19.json`](raw/JCOP4-pace-gm-2026-11-19.json) | `7f2275332bbb5f73ce993a6ac787b613d987d194b9403cb30a3eb6e43e22eae5` | PARTIAL: 13/30 operation categories verified; original PACE/XY failed |
| [`JCOP4-pace-k1-2026-11-19.json`](raw/JCOP4-pace-k1-2026-11-19.json) | `a4ee96954f95a0fc8ea3d30a56f9d26bfb43a0fcb34eaceb034ee272b76acaef` | PASS: 50/50 published PACE vectors; 150.046 ms median |

The two `PARTIAL` files report verified *operation categories* with repeated attempts; `11/18` and `13/30` must not be described as raw APDU success ratios. The successful and failed operations can be inspected individually in the original JSON.

No raw card serial, ATR, CPLC, GlobalPlatform keys or wallet secrets were added during import; the reports contain the original AIDs, public test vectors, benchmark metadata, and local developer build path strings. Review public metadata policies before further redistribution. Never turn a `6F02` into a success or claim that a separate `4E01` applet has been physically tested.

Run `python3 -B -m unittest discover -s RAILGUN/tests -p 'test_jcop4_raw_benchmarks.py' -v` to verify the pinned SHA-256 hashes, source data structure and reported aggregate values. This tests **artifact integrity and internal consistency**, not cryptographic correctness on JCOP4 and not original capture provenance.
