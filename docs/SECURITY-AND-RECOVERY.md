# Security and Recovery Findings

Updated: November 2, 2026

## 1. Hardware ECDSA signing works

The physical retail Keycard successfully signs Ethereum
digests using its existing hardware-held private key.

Independent ECDSA verification and public-key recovery
matched the exported hardware account after correcting
the Keycard Go signature parser.

This establishes cryptographic interoperability, not
end-to-end security of a production wallet application.

## 2. Legacy SDK signature corruption

Keycard Go's legacy response handling originally combined
R and S using an append operation on overlapping slices.

This could overwrite the S component while calculating
the recovery identifier.

The corrected implementation copies R before concatenation.

See:
https://github.com/keycard-tech/keycard-go/pull/20

The fix has merged into upstream develop.

## 3. ECDSA signature determinism

The Keycard developer confirmed that native JavaCard ECDSA
uses a random signing nonce (k).

Consequently, repeated signatures over the same digest
need not produce identical R/S values.

The initial determinism experiment used the unpatched
SDK, whose signature output was affected by the parser
bug. That output alone should not be treated as a valid
independent deterministic-signature test.

The developer's explanation establishes that the native
signing mode is randomized.

## 4. Privacy Pools implications

Signature-derived note or credential recovery requires
a reproducible secret derivation process.

The current randomized ECDSA signing mode does not provide
reproducible signature bytes for this purpose.

Therefore, do not derive persistent Privacy Pools note
secrets from ordinary Keycard ECDSA signature bytes.

The hardware signer can still authorize Ethereum
transactions independently of privacy-note recovery.

Privacy Pools, Railgun, and other ZK systems may require
additional secret material on the host for note handling
or proving. Hardware transaction signing does not imply
those protocol secrets remain isolated on the card.

Kohaku's privacy keystore and `deriveAt` interfaces remain
separate from our hardware signing work.

## 5. Retail Keycard blind signing

The tested retail Keycard signs a host-supplied digest.

It does not independently display the transaction
recipient, value, network, or contract call.

A compromised host could request a signature for a digest
different from the transaction the user believes is being
approved.

Local signature verification proves which key signed the
digest. It does not establish informed user approval of
the digest's underlying transaction.

## 6. Prototype PIN handling

The prototype passes the PIN through KEYCARD_PIN in the
child-process environment.

Environment variables are not an appropriate production
secret-handling mechanism.

The prototype also depends on an externally built
Keycard CLI binary. That binary is trusted code in the
current architecture.

Future work must improve secret entry, command execution,
device selection, timeout behavior, and error handling.

## 7. EIP-7702 delegation

An EIP-7702 authorization can delegate account execution
to smart-contract code.

The current adapter signs authorizations but does not
activate delegation during tests.

The adapter rejects chain ID zero as a local policy.
EIP-7702 itself permits chain-independent authorizations
using chain ID zero.

Delegation changes the account's execution security
boundary. Delegate implementations must be assessed
before production use.

## 8. Verification versus execution

Verified locally:
- Ethereum message and typed-data signatures
- Serialized transaction signatures
- EIP-7702 authorization signatures
- Offline Simple7702 UserOperation signatures

Not established:
- Safe live transaction broadcasting
- Production UserOperation/bundler compatibility
- User-confirmed transaction intent
- Device-disconnection and retry handling
- Secure unattended or multi-device operation

No private key was exported and no transaction was
broadcast in these experiments.
