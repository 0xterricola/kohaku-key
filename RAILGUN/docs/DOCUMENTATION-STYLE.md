# RAILGUN documentation conventions

This file defines editorial conventions for the `RAILGUN/` research documentation. It does not replace experiment-specific safety instructions or change original benchmark evidence.

## Document roles

| Location | Purpose | Update policy |
| --- | --- | --- |
| [`README.md`](../README.md) | Current project status and navigation | Update with meaningful research milestones |
| [`docs/ROADMAP.md`](ROADMAP.md) | Next experiments, exit criteria, and paused tracks | Keep forward-looking claims explicit |
| [`benchmarks/HARDWARE-LEADERBOARD.md`](../benchmarks/HARDWARE-LEADERBOARD.md) | Fastest verified *within a measured workload and timing scope* | Cite source data; never imply theoretical optimality |
| [`benchmarks/RESULTS.md`](../benchmarks/RESULTS.md) | Historical and contemporary measured results | Label superseded baselines |
| `benchmarks/<experiment>/` and `experiments/<experiment>/` | Experiment procedures and evidence | Preserve historical statements as dated observations; add follow-up notes rather than rewriting raw data |
| [`docs/RAILGUN-SHELL-STUDY-GUIDE.md`](RAILGUN-SHELL-STUDY-GUIDE.md) | Historical source-specific technical study | Preserve the source commit and snapshot scope |
| [`HARDWARE-SAFETY.md`](../HARDWARE-SAFETY.md) and [`docs/SECURITY.md`](SECURITY.md) | Hardware and protocol security boundaries | Update only with supported guarantees |

## Markdown and navigation

- Use one descriptive `#` heading, followed by a short scope or status paragraph. Use `##` for major topics and `###` for subordinate material; avoid skipping heading levels.
- Prefer sentence-case headings, consistent terminology, Markdown links to local documents, and repository-root-relative commands in fenced `sh` blocks.
- Use ISO `YYYY-MM-DD` dates for experiments. Present metadata as bullets or a table, rather than relying on trailing spaces for line breaks.
- Keep source code, APDU bytes, identifiers, AIDs, file names, tool output, and original machine-readable benchmark evidence byte-for-byte intact.
- Check relative links against tracked files. Do not replace links to unavailable historical artifacts with invented URLs or files.

Run the read-only documentation check from repository root:

```sh
python3 -B RAILGUN/scripts/check_documentation.py
```

## Cryptographic terminology and claims

- In narrative prose, use **BabyJubJub**, **Poseidon T3**/**Poseidon T6**, **PACE-GM**, **JCOP3**/**JCOP4**, **PC/SC**, **JavaCard**, **CAP**, and **SHA-256**. Preserve historical source names and code identifiers exactly.
- Distinguish **public-input arithmetic tests**, **simulator tests**, **physical hardware correctness**, **complete signing**, and **production security**. Passing one category is not evidence for another.
- A cross-generation speed comparison must state the reader, host, applet variant, operation, and timing boundary. Never attribute a measured ratio solely to chip generation unless those variables are controlled.
- Keep `4D01` (Mikkoph's physically tested K=1 applet) separate from `4E01` (locally built, offline validated, physical execution pending as of 2026-11-24).
- For signer prototypes, distinguish **synthetic-key signing**, **private-scalar isolation during signing**, **secure key provisioning**, **host challenge/transaction binding**, **nonce/session security**, and **trusted approval**.

## Benchmark reporting

For new benchmarks, record the experiment/date, card generation, reader, JavaCard/provider, package and applet AIDs, CAP/source fingerprints, operation and input class, vector count, exact-match count, raw evidence provenance, timing metric and boundary, and failed or unsupported operations. Report the number of samples and use medians only for repeated observations.

Label reported summaries that lack original per-sample traces. Do not fabricate missing JSON samples, calculate statistical confidence from single runs, equate `PARTIAL` operation categories with APDU failure ratios, or silently replace archived historical results.

For the current measured baseline and its caveats, see the [hardware leaderboard](../benchmarks/HARDWARE-LEADERBOARD.md).

## Command and card safety

Label each command **offline** or **physical APDUs**. Physical runners require an explicit dedicated test card and must not automatically install, initialize, delete, or personalize applets. Never publish wallet secrets, PINs, master keys, GlobalPlatform credentials, or raw identifying card metadata. Preserve the existing [hardware safety requirements](../HARDWARE-SAFETY.md).
