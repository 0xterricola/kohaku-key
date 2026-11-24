# Poseidon T3 RSA-5 Barrett — 7F

Experimental JCOP3 JavaCard Poseidon implementation.

- **Package AID:** `F0424E3235347F00`
- **Applet AID:** `F0424E3235347F01`
- **CAP SHA-256:** `be1c0cb797624ba50235e9b26086f8f2c18b6c1e0917a8d28335634182ac71f0`

## Protocol

SELECT:

`00A4040008F0424E3235347F01`

Initialize a canonical test vector:

`80 7D <index> 00 01`

Execute the next Poseidon round:

`80 7E 00 00 60`

Each round returns 96 bytes representing three canonical
32-byte big-endian field elements.

Vector indices:

| Index | Vector |
| ---: | --- |
| 0 | `zero` |
| 1 | `one-two` |
| 2 | `three-five` |
| 3 | `mixed` |
| 4 | `boundary` |

## Offline reference verification

From the repository root:

    python3 -B RAILGUN/scripts/poseidon_t3_7f.py --self-test

Expected: 325/325 reference rounds and five final hashes.

No smart-card access occurs during this test.

## Physical reproduction

Install pyscard and use a compatible research-only card
with the exact 7F applet already installed.

Run:

    python3 -B RAILGUN/scripts/poseidon_t3_7f.py \
      --hardware --confirm-test-card \
      --reader "HID Global OMNIKEY 3x21 Smart Card Reader" \
      --platform "JCOP3" \
      --vector one-two \
      --cap /path/to/pinned-7f.cap \
      --output /path/to/7f-one-two.json

Replace the reader name with the exact PC/SC name.

The runner never installs, deletes, personalizes or
authenticates a wallet.

It validates the local CAP fingerprint, not the contents
of the installed smart card.

Other platforms require independent correctness and
latency validation.

## Publication scope

The original CAP and reconstructed arithmetic source
are not redistributed in this checkpoint.

Offline reference tests are independently runnable.
Exact physical reproduction additionally requires
access to the pinned binary and compatible hardware.

See the benchmark report:

[7F physical result](../../benchmarks/poseidon-t3-rsa5-7f-2026-11-23/README.md)
