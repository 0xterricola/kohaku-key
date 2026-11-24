# Verified hardware performance index — 2026-11-23

**Purpose:** one entry point for the fastest *measured, verified* research implementations. It is not a device-wide benchmark ranking, a security certification, or a signing throughput claim. Timing scopes differ; compare within the documented test method only.

## JCOP3 — fastest observed results by operation

| Operation | Implementation / AID | Result | Verification | Measurement scope | Evidence |
| --- | --- | ---: | --- | --- | --- |
| **Poseidon T3 full 2-input hash** | **RSA-5 7E**, `F0424E3235347E01` | **~230.520 s/hash**, reported five-vector result; pinned `one-two` **230.716374 s** | 5/5 hashes, 325/325 states | Physical PC/SC; original vector records retained for 2 runs | [7E baseline](poseidon-t3-rsa5-7e-2026-11-21/README.md) · [raw experiments](../experiments/poseidon-t3-rsa5-jcop3-2026-11-21/RESULTS.md) |
| Poseidon T3, Barrett candidate | 7F, `F0424E3235347F01` | 255.289453 s, `one-two` | 65/65 states; one physical vector | Host elapsed, not an identical timing boundary to 7E | [7F benchmark](poseidon-t3-rsa5-7f-2026-11-23/README.md) |
| Native BabyJubJub scalar multiplication | Weierstrass native ECC | 207.989 ms, fixed 251-bit `KB`, initial median | 20/20 initial full-point tests covering 2B / KB | Initial host-observed benchmark; **not** PC/SC-only | [RAILGUN results](../README.md) |
| Native BabyJubJub scalar multiplication, warm workflow | Weierstrass native ECC | 352.742 ms, `KB` | 50/50 interleaved warm-session operations across ECC and PACE | CLI + SELECT + transport + card | [warm session](RESULTS.md) |
| PACE-GM public point addition | `3C01` JCOP3 research applet | **222.923 ms** median | 10/10 vector matches | PC/SC transmit only | [physical replay](RESULTS.md) |
| RSA-backed BN254 modular squaring, dense inputs | Single RSA exponent-2 square + reduction | **~550 ms** | 120/120 APDUs across archival RSA experiments | Historical physical, workload-specific | [BN254 evidence](../README.md) |

**7E is the fastest measured on-card Poseidon T3 full hash** in this research, not necessarily the fastest theoretically possible RSA-5 implementation. 7E's on-card applet was retired to install 7F; its CAP identity, offline fixtures, and physical evidence remain archived. A ~362.363 s earlier baseline was about 1.57× slower. The five-vector ~230.520 s figure is a reported result; only two original per-run JSON timing records are retained in the repository.

## JCOP4 — independent physical results (Mikkoph / bitgamma, Nov 19)

| Operation | Tested implementation / AID | Physical result | Verification | Notes |
| --- | --- | ---: | --- | --- |
| Native scalar multiplication, X only, 251-bit public scalar | `3701` native-ec | **85.706 ms** median, 10 repeats | 10/10 for `plain_wide_5` | PC/SC transmit; X only, not full XY |
| Native scalar multiplication, X only, 251-bit public scalar | `3C01` original pace-gm | **85.771 ms** median, 10 repeats | 10/10 for `plain_wide_5` | Independent second applet |
| PACE-GM public point addition | **`4D01` K=1 variant** | **150.046 ms** median, min 149.144, max 168.936 | 50/50 vectors exact, SW 9000 | PC/SC transmit; excludes SELECT/initialization |
| RSA-1024 modular exponentiation, exponent 3 | `3C01` probe | **241.751 ms** median | 10/10 responses | **Not** comparable to JCOP3 BN254 exponent-2 squaring |
| Full XY / PACE on original applets | `3701` / `3C01` | `6F02` | Failed as published | Requires provider-specific curve initialization investigation |
| Original 4E K=1 compatibility variant | `4E01` | **Not measured** | Offline validated, physical test pending | Do not conflate with Mikkoph's tested `4D01` |
| Complete BabyJubJub EdDSA-Poseidon signature | — | **Not demonstrated** | — | JCOP3 and JCOP4 both pending |

Raw JCOP4 evidence and fingerprints: [independently supplied four JSON reports](jcop4-2026-11-19/README.md). Attribution: [Mikkoph's developer report](https://gist.github.com/bitgamma/18bed236b7073b8b951f26ba68e76515). The per-APDU JCOP3 PACE replay (222.923 ms) and JCOP4 K=1 PACE result (150.046 ms) both use PC/SC transmit; the ~1.486× ratio compares *different readers, hosts, applets, and cards*, not isolated chip speed. Do not mix these with JCOP3 warm CLI-inclusive latency.

## Selection rules / unmeasured claims

- **Fastest** means fastest measured within the stated workload and timing scope; use the verified median for repeated trials, otherwise label single-run / reported measurements.
- Distinguish `PASS` from `PARTIAL`, unsuccessful operations, simulator estimates and theoretical speedups.
- No secret spending scalar, wallet PIN, production signatures, side-channel claim, or on-device approval was tested in the cited primitive benchmarks.
- A fully working **two-phase COMMIT/RESPOND signing session** is now the primary goal. Preserve RSA-5 as a documented feasibility baseline, not the current signing critical path.
- Recheck this index when physical `4E01` results or local JCOP4 cards become available.
