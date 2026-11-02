# Signature Determinism Experiment

First experiment: sign the same canonical EIP-712 envelope
repeatedly using the target hardware and derivation path.

Compare r and normalized low-s, not raw transport framing.
Repeat across sessions and record firmware versions.

Compare with software signing separately. Matching public keys
alone does not establish privacy credential compatibility.

Use disposable test keys only.
