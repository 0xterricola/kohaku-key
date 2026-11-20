# JavaCard research applet error diagnostics

## Exception mapping

The published PACE-GM applet maps CryptoException reasons
from ordinary cryptographic commands as:

    0x6F00 | (reason & 0x0F)

| Status | Research applet meaning |
| --- | --- |
| 6F01 | CryptoException.ILLEGAL_VALUE |
| 6F02 | CryptoException.UNINITIALIZED_KEY |
| 6F03 | CryptoException.NO_SUCH_ALGORITHM |
| 6F04 | CryptoException.INVALID_INIT |
| 6F05 | CryptoException.ILLEGAL_USE |

These are applet-defined status mappings, not universal
ISO 7816 or GlobalPlatform definitions.

## Initialization step failures

During initialization the applet encodes exceptions as:

    CryptoException:
    0x6F00 | ((step & 15) << 4) | (reason & 15)

    SystemException:
    0x6E00 | ((step & 15) << 4) | (reason & 15)

Examples in initialization context:

- 6F72: step 7, CryptoException reason 2
- 6E72: step 7, SystemException reason 2

Do not infer initialization steps from ordinary
vector responses.

The physical PACE benchmark runner does not
perform applet initialization.

## Standard and contextual status words

| Status | General interpretation |
| --- | --- |
| 9000 | Success |
| 6700 | Wrong length |
| 6985 | Conditions of use not satisfied |
| 6A80 | Incorrect command data |
| 6A86 | Incorrect P1/P2 |
| 6A88 | Referenced data not found |
| 6D00 | Instruction not supported |
| 6E00 | CLA not supported |

GlobalPlatform INSTALL returning 6985 does not
establish whether the applet constructor executed.

## JCOP4 PACE-GM discovery

Mikkoph observed 6F02 on the published PACE-GM
applet on JCOP4. Explicitly setting K=1 allowed
his separate experimental applet to reproduce
the public vectors.

K=1 is a provider compatibility setting, not
the research curve's mathematical cofactor (8).

The local 4E00 variant remains unverified on
physical JCOP4 hardware.

## Troubleshooting

For 6F02, inspect the selected research applet,
its initialization, and provider configuration.

For 6F03, inspect the requested KeyAgreement
algorithm and provider support.

For 6985, inspect the operation context and
lifecycle conditions. Do not guess which
resource or constructor operation failed.

Stop on unexpected responses. Do not automatically
retry, reset, install, or delete card contents.
