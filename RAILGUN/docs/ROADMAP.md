# RAILGUN hardware research — measured execution roadmap

Updated: November 23, 2026. Independent research; no secure production signer is claimed.

## Priority 1 — Confirm JCOP4 compatibility while JCOP3 work continues

Completed: native BabyJubJub ECC and PACE-GM public-point verification on JCOP3. Independent JCOP4 `4D01` PACE-GM result 50/50 PASS at 150.046 ms median. Original JCOP4 applets failed PACE-GM/XY with `6F02`, localized to provider cofactor initialization. Four original JCOP4 JSON files have been imported with SHA-256 checks and author attribution.

Pending: Mikkoph's physical check of locally built `4E00/4E01` (not the tested `4D01`), independent reproduction on newly arrived JCOP4 cards, transport-matched cross-generation measurements, and analysis of the security effects of provider-specific `K=1` use.

## Priority 2 — Two-phase BabyJubJub signing (current critical path)

Start with ZKNOX/keycard-sim's COMMIT/RESPOND design. Verify randomized EdDSA-Poseidon offline using synthetic keys, exact RAILGUN verifier behavior, nonce lifecycle, rejection and reset behavior, single-use sessions, challenge binding and ROS threat model. Then perform one carefully scoped physical JCOP3 signing experiment, with no valuable keys or funds. Replicate on JCOP4 when available. Card must never accept unsafe host-controlled challenges that permit nonce reuse or unauthorized signatures.

**Exit:** verified full signatures and negative tests, with separately recorded PC/SC, host Poseidon, session setup and end-to-end latency. A demo does not prove security against a compromised host.

## Priority 3 — Keycard Shell integration and progressive hardening

Coordinate with Keycard product developers and RAILGUN researchers after JCOP4 feasibility. Separate research-only blind-signing over a host/phone from a hardened device approval flow with secure transaction intent verification. Define spending-key provisioning and recovery boundary: host software seeing key material during provisioning is distinct from key isolation during later signing. Do not claim fully isolated spending keys until provisioning is addressed.

## Paused track — On-card Poseidon arithmetic

Validated JCOP3 Poseidon T3 7E RSA-5 at ~230.520 s reported across five vectors, 325/325 physical rounds; 7F Barrett at 255.289453 s for one vector, 65/65. Both documented; 7F slower by 10.65% against pinned `one-two` 7E record. This is **not** a practical on-card RAILGUN T6 signing-challenge implementation. Resume only with isolated profile evidence for a substantial gain or an architecture requirement that cannot be fulfilled by the trusted host/Shell boundary.

## Reference evidence

- [Hardware leaderboard](../benchmarks/HARDWARE-LEADERBOARD.md)
- [JCOP4 raw evidence and hashes](../benchmarks/jcop4-2026-11-19/README.md)
- [Poseidon T3 7E](../benchmarks/poseidon-t3-rsa5-7e-2026-11-21/README.md)
- [Poseidon T3 7F](../benchmarks/poseidon-t3-rsa5-7f-2026-11-23/README.md)
- [ZKNOX signing prototype](https://github.com/ZKNoxHQ/keycard-sim)
