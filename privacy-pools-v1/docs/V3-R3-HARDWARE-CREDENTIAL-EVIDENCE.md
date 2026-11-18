# V3-R3 — Physical Keycard Privacy Pools Credential Reconstruction

Status: Offline physical hardware proof of concept passed.

## Hardware

- Experimental Phonon DAO Keycard
- Applet 4.0
- HID Global OMNIKEY 3x21 reader
- Certificate verified against Keycard test CA
- Interactive PIN authentication
- Two independent authenticated sessions

## Architecture

Keycard 4.0 BIP-85
  -> runtime-only derived entropy
  -> versioned HMAC derivation adapter
  -> legacy Privacy Pools SecretManager
  -> reproducible note credentials

BIP-85 material is transferred from Go to Node using
an anonymous pipe, without intentional disk persistence.

This adapter does not implement BIP-32 derivation.

## Physical results

- Hardware-derived root reproduced: PASS
- Deposit credentials reproduced: PASS
- Withdrawal credentials reproduced: PASS
- Ephemeral signer reproduced: PASS
- Deposit index separation: PASS
- Chain separation: PASS

All operations were performed offline.

## Security boundaries

- No real private keys were intentionally exported.
- No derived entropy or credential secrets were logged.
- No blockchain transactions were executed.
- Secret material enters host process memory.
- Go and Node do not guarantee complete memory erasure.
- Test CA authentication is not a production trust policy.
- Recovery after card loss was not tested.
- Default Privacy Pools keystore compatibility is unproven.
- Live deposit and withdrawal execution was not tested.

## Next research

1. Specify the versioned credential derivation contract.
2. Test recovery across application restarts.
3. Evaluate card-loss and backup recovery requirements.
4. Review memory handling and secret exposure boundaries.
5. Design integration without modifying frozen V2 code.

Do not use the experimental credential scheme for
real funds before recovery and security validation.
