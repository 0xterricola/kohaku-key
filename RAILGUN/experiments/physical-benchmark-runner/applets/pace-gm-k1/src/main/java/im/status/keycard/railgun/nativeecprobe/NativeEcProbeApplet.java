
package im.status.keycard.railgun.nativeecprobe;

import javacard.framework.APDU;
import javacard.framework.Applet;
import javacard.framework.ISO7816;
import javacard.framework.ISOException;
import javacard.framework.Util;
import javacard.framework.SystemException;
import javacard.security.CryptoException;
import javacard.security.ECPrivateKey;
import javacard.security.KeyAgreement;
import javacard.security.KeyBuilder;

import javacard.security.RSAPublicKey;
import javacardx.crypto.Cipher;

public final class NativeEcProbeApplet extends Applet {

    private static final byte[] PROBE_ONE = {(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x01};
    private static final byte[] PROBE_RSA_MODULUS = {(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF,(byte)0xFF};
    private static final byte[] PROBE_RSA_EXP = {(byte)0x03};

    private KeyAgreement paceProbe;
    private final byte[] paceInput;
    private RSAPublicKey rsaProbeKey;
    private Cipher rsaProbeCipher;

    private static final byte[] BENCH_K = {(byte)0x04,(byte)0x5C,(byte)0xB4,(byte)0x31,(byte)0x28,(byte)0x16,(byte)0x01,(byte)0x97,(byte)0x77,(byte)0xED,(byte)0x79,(byte)0xB2,(byte)0x02,(byte)0xC1,(byte)0xB1,(byte)0x27,(byte)0x32,(byte)0xFF,(byte)0x07,(byte)0x96,(byte)0x8A,(byte)0x8C,(byte)0xDD,(byte)0x28,(byte)0x1F,(byte)0x9A,(byte)0xA5,(byte)0x3D,(byte)0xFA,(byte)0x0B,(byte)0xF3,(byte)0x48};

    private static final byte[] FIELD = new byte[] {(byte)0x30, (byte)0x64, (byte)0x4e, (byte)0x72, (byte)0xe1, (byte)0x31, (byte)0xa0, (byte)0x29, (byte)0xb8, (byte)0x50, (byte)0x45, (byte)0xb6, (byte)0x81, (byte)0x81, (byte)0x58, (byte)0x5d, (byte)0x28, (byte)0x33, (byte)0xe8, (byte)0x48, (byte)0x79, (byte)0xb9, (byte)0x70, (byte)0x91, (byte)0x43, (byte)0xe1, (byte)0xf5, (byte)0x93, (byte)0xf0, (byte)0x00, (byte)0x00, (byte)0x01};
    private static final byte[] CURVE_A = new byte[] {(byte)0x10, (byte)0x21, (byte)0x6f, (byte)0x7b, (byte)0xa0, (byte)0x65, (byte)0xe0, (byte)0x0d, (byte)0xe8, (byte)0x1a, (byte)0xc1, (byte)0xe7, (byte)0x80, (byte)0x80, (byte)0x72, (byte)0xc9, (byte)0xb8, (byte)0x11, (byte)0x4d, (byte)0x6d, (byte)0x7d, (byte)0xe8, (byte)0x7a, (byte)0xdb, (byte)0x16, (byte)0xa0, (byte)0xa7, (byte)0x2f, (byte)0x1a, (byte)0x91, (byte)0xf6, (byte)0xa0};
    private static final byte[] CURVE_B = new byte[] {(byte)0x23, (byte)0xd8, (byte)0x85, (byte)0xf6, (byte)0x47, (byte)0xfe, (byte)0xd5, (byte)0x74, (byte)0x3c, (byte)0xad, (byte)0x3d, (byte)0x1e, (byte)0xe4, (byte)0xab, (byte)0xa9, (byte)0xc0, (byte)0x43, (byte)0xb4, (byte)0xac, (byte)0x0f, (byte)0xc2, (byte)0x76, (byte)0x66, (byte)0x58, (byte)0xa4, (byte)0x10, (byte)0xef, (byte)0xde, (byte)0xb2, (byte)0x1f, (byte)0x70, (byte)0x6e};
    private static final byte[] BASE = new byte[] {(byte)0x04, (byte)0x1f, (byte)0xde, (byte)0x0a, (byte)0x3c, (byte)0xac, (byte)0x7c, (byte)0xb4, (byte)0x6b, (byte)0x36, (byte)0xc7, (byte)0x9f, (byte)0x4c, (byte)0x0a, (byte)0x7a, (byte)0x73, (byte)0x2e, (byte)0x38, (byte)0xc2, (byte)0xc7, (byte)0xee, (byte)0x9a, (byte)0xc4, (byte)0x1f, (byte)0x44, (byte)0x39, (byte)0x2a, (byte)0x07, (byte)0xb7, (byte)0x48, (byte)0xa0, (byte)0x86, (byte)0x9f, (byte)0x20, (byte)0x3a, (byte)0x71, (byte)0x01, (byte)0x60, (byte)0x81, (byte)0x1d, (byte)0x5c, (byte)0x07, (byte)0xeb, (byte)0xae, (byte)0xb8, (byte)0xfe, (byte)0x1d, (byte)0x9c, (byte)0xe2, (byte)0x01, (byte)0xc6, (byte)0x6b, (byte)0x97, (byte)0x0d, (byte)0x66, (byte)0xf1, (byte)0x8d, (byte)0x0d, (byte)0x2b, (byte)0x26, (byte)0x4c, (byte)0x19, (byte)0x53, (byte)0x09, (byte)0xaa};
    private static final byte[] ORDER = new byte[] {(byte)0x06, (byte)0x0c, (byte)0x89, (byte)0xce, (byte)0x5c, (byte)0x26, (byte)0x34, (byte)0x05, (byte)0x37, (byte)0x0a, (byte)0x08, (byte)0xb6, (byte)0xd0, (byte)0x30, (byte)0x2b, (byte)0x0b, (byte)0xab, (byte)0x3e, (byte)0xed, (byte)0xb8, (byte)0x39, (byte)0x20, (byte)0xee, (byte)0x0a, (byte)0x67, (byte)0x72, (byte)0x97, (byte)0xdc, (byte)0x39, (byte)0x21, (byte)0x26, (byte)0xf1};
    private static final byte[] TWO = new byte[] {(byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x02};
    private static final byte[] THREE = new byte[] {(byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x03};

    private static final byte[] WIDE_0 = new byte[] {(byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x02};
    private static final byte[] WIDE_1 = new byte[] {(byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x03};
    private static final byte[] WIDE_2 = new byte[] {(byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x11};
    private static final byte[] WIDE_3 = new byte[] {(byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x80, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x01, (byte)0x35, (byte)0x79};
    private static final byte[] WIDE_4 = new byte[] {(byte)0x01, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x01, (byte)0x23, (byte)0x45};
    private static final byte[] WIDE_5 = new byte[] {(byte)0x06, (byte)0x0C, (byte)0x89, (byte)0xCE, (byte)0x5C, (byte)0x26, (byte)0x34, (byte)0x05, (byte)0x37, (byte)0x0A, (byte)0x08, (byte)0xB6, (byte)0xD0, (byte)0x30, (byte)0x2B, (byte)0x0B, (byte)0xAB, (byte)0x3E, (byte)0xED, (byte)0xB8, (byte)0x39, (byte)0x20, (byte)0xEE, (byte)0x0A, (byte)0x67, (byte)0x72, (byte)0x97, (byte)0xDC, (byte)0x39, (byte)0x21, (byte)0x26, (byte)0xF0};
    private ECPrivateKey key;
    private KeyAgreement agreement;
    private KeyAgreement xyAgreement;
    private byte stage;

    private NativeEcProbeApplet() {
        paceInput = javacard.framework.JCSystem.makeTransientByteArray((short)65, javacard.framework.JCSystem.CLEAR_ON_DESELECT);

        register();
    }

    public static void install(byte[] data, short offset, byte length) {
        new NativeEcProbeApplet();
    }

    public void process(APDU apdu) {
        if (selectingApplet()) return;

        byte[] b = apdu.getBuffer();

        if (b[ISO7816.OFFSET_CLA] != (byte)0x80) {
            ISOException.throwIt(ISO7816.SW_CLA_NOT_SUPPORTED);
        }


        // Public-scalar benchmark; never reads wallet keys.
        if (b[ISO7816.OFFSET_INS] == (byte)0x72) {
            if (stage != (byte)11 ||
                    b[ISO7816.OFFSET_P1] != (byte)0 ||
                    b[ISO7816.OFFSET_P2] != (byte)0) {
                ISOException.throwIt(
                    ISO7816.SW_CONDITIONS_NOT_SATISFIED);
            }
            try {
                short n = agreement.generateSecret(
                    BASE, (short)0, (short)65,
                    b, (short)0);
                apdu.setOutgoingAndSend((short)0, n);
            } catch (CryptoException e) {
                ISOException.throwIt((short)(
                    0x6F00 | (e.getReason() & 0x0F)));
            }
            return;
        }

        // No-op APDU baseline.
        if (b[ISO7816.OFFSET_INS] == (byte)0x73) {
            if (stage != (byte)11) {
                ISOException.throwIt(
                    ISO7816.SW_CONDITIONS_NOT_SATISFIED);
            }
            b[0] = (byte)0;
            apdu.setOutgoingAndSend((short)0, (short)1);
            return;
        }

        // Select only public test scalars 2 and 3.
        if (b[ISO7816.OFFSET_INS] == (byte)0x74) {
            byte s = b[ISO7816.OFFSET_P1];
            if (stage != (byte)11 ||
                    b[ISO7816.OFFSET_P2] != (byte)0 ||
                    (s != (byte)2 && s != (byte)3)) {
                ISOException.throwIt(
                    ISO7816.SW_INCORRECT_P1P2);
            }
            try {
                byte[] value = s == (byte)2 ? TWO : THREE;
                key.setS(value, (short)0, (short)32);
                agreement.init(key);
                b[0] = s;
                apdu.setOutgoingAndSend((short)0, (short)1);
            } catch (CryptoException e) {
                ISOException.throwIt((short)(
                    0x6F00 | (e.getReason() & 0x0F)));
            }
            return;
        }


        // Fixed public test vectors only; no host-supplied secret scalars.
        if (b[ISO7816.OFFSET_INS] == (byte)0x75) {
            if (stage != (byte)11 ||
                    b[ISO7816.OFFSET_P2] != (byte)0) {
                ISOException.throwIt(ISO7816.SW_CONDITIONS_NOT_SATISFIED);
            }

            byte which = b[ISO7816.OFFSET_P1];
            byte[] value;
            if (which == (byte)0) value = WIDE_0;
            else if (which == (byte)1) value = WIDE_1;
            else if (which == (byte)2) value = WIDE_2;
            else if (which == (byte)3) value = WIDE_3;
            else if (which == (byte)4) value = WIDE_4;
            else if (which == (byte)5) value = WIDE_5;
            else {
                ISOException.throwIt(ISO7816.SW_INCORRECT_P1P2);
                return;
            }

            try {
                key.setS(value, (short)0, (short)32);
                agreement.init(key);
                short n = agreement.generateSecret(
                    BASE, (short)0, (short)65, b, (short)0);
                apdu.setOutgoingAndSend((short)0, n);
            } catch (CryptoException e) {
                ISOException.throwIt((short)(
                    0x6F00 | (e.getReason() & 0x0F)));
            }
            return;
        }



        // Full-width XY: six fixed public scalars.


        // M2.31c.3: Ten distinct public H points supplied by host.
        // PACE Generic Mapping computes s*G + H, with fixed s=1.
        // No wallet key, PIN or host-supplied secret scalar.
        if (b[ISO7816.OFFSET_INS] == (byte)0x77) {
            if (stage != (byte)11 ||
                b[ISO7816.OFFSET_P1] != (byte)0 ||
                b[ISO7816.OFFSET_P2] != (byte)0) {
                ISOException.throwIt(
                    ISO7816.SW_CONDITIONS_NOT_SATISFIED);
            }

            if ((short)(b[ISO7816.OFFSET_LC] & 0xff)
                != (short)65) {
                ISOException.throwIt(ISO7816.SW_WRONG_LENGTH);
            }

            short total = (short)0;
            short received = apdu.setIncomingAndReceive();

            while (received > (short)0) {
                if ((short)(total + received) > (short)65) {
                    ISOException.throwIt(ISO7816.SW_WRONG_LENGTH);
                }

                javacard.framework.Util.arrayCopyNonAtomic(
                    b, ISO7816.OFFSET_CDATA,
                    paceInput, total, received);

                total = (short)(total + received);
                if (total == (short)65) break;
                received = apdu.receiveBytes(
                    ISO7816.OFFSET_CDATA);
            }

            if (total != (short)65) {
                ISOException.throwIt(ISO7816.SW_WRONG_LENGTH);
            }

            try {
                if (paceProbe == null) {
                    paceProbe = KeyAgreement.getInstance(
                        (byte)0x05, false);
                }

                key.setS(PROBE_ONE, (short)0, (short)32);
                paceProbe.init(key);

                short n = paceProbe.generateSecret(
                    paceInput, (short)0, (short)65,
                    b, (short)0);

                apdu.setOutgoingAndSend((short)0, n);
                return;
            } catch (CryptoException e) {
                ISOException.throwIt(
                    (short)(0x6F00 | (e.getReason() & 0x0F)));
            }
            return;
        }

    // M2.30r: PUBLIC RSA coprocessor capability.
        // P1=0 initializes a 1024-bit RSA public key.
        // P1=1 computes 2^3 mod N, returning 128 bytes.
        // This is NOT yet a JCMathLib field operation.
        if (b[ISO7816.OFFSET_INS] == (byte)0x79) {
            if (stage != (byte)11 ||
                b[ISO7816.OFFSET_P2] != (byte)0) {
                ISOException.throwIt(
                    ISO7816.SW_CONDITIONS_NOT_SATISFIED);
            }

            byte whichRSA = b[ISO7816.OFFSET_P1];

            if (whichRSA != (byte)0 &&
                whichRSA != (byte)1) {
                ISOException.throwIt(
                    ISO7816.SW_INCORRECT_P1P2);
            }

            try {
                if (rsaProbeKey == null) {
                    rsaProbeKey = (RSAPublicKey)
                        KeyBuilder.buildKey(
                            KeyBuilder.TYPE_RSA_PUBLIC,
                            KeyBuilder.LENGTH_RSA_1024,
                            false);

                    rsaProbeKey.setModulus(
                        PROBE_RSA_MODULUS,
                        (short)0, (short)128);
                    rsaProbeKey.setExponent(
                        PROBE_RSA_EXP,
                        (short)0, (short)1);
                }

                if (rsaProbeCipher == null) {
                    rsaProbeCipher = Cipher.getInstance(
                        Cipher.ALG_RSA_NOPAD, false);
                }

                if (whichRSA == (byte)0) {
                    b[0] = (byte)1;
                    apdu.setOutgoingAndSend(
                        (short)0, (short)1);
                    return;
                }

                rsaProbeCipher.init(
                    rsaProbeKey, Cipher.MODE_ENCRYPT);

                Util.arrayFillNonAtomic(
                    b, (short)0, (short)128, (byte)0);
                b[127] = (byte)2;

                short n = rsaProbeCipher.doFinal(
                    b, (short)0, (short)128,
                    b, (short)0);

                apdu.setOutgoingAndSend((short)0, n);
                return;

            } catch (CryptoException e) {
                ISOException.throwIt((short)(
                    0x6F00 | (e.getReason() & 0x0F)));
            }
            return;
        }

        if (b[ISO7816.OFFSET_INS] == (byte)0x76) {
            if (stage != (byte)11 ||
                    b[ISO7816.OFFSET_P2] != (byte)0) {
                ISOException.throwIt(
                    ISO7816.SW_CONDITIONS_NOT_SATISFIED);
            }

            byte which = b[ISO7816.OFFSET_P1];
            byte[] value;
            if (which == (byte)0) value = WIDE_0;
            else if (which == (byte)1) value = WIDE_1;
            else if (which == (byte)2) value = WIDE_2;
            else if (which == (byte)3) value = WIDE_3;
            else if (which == (byte)4) value = WIDE_4;
            else if (which == (byte)5) value = WIDE_5;
            else if (which == (byte)6) value = BENCH_K;
            else {
                ISOException.throwIt(ISO7816.SW_INCORRECT_P1P2);
                return;
            }

            try {
                if (xyAgreement == null) {
                    xyAgreement =
                        KeyAgreement.getInstance((byte)0x06, false);
                }

                key.setS(value, (short)0, (short)32);
                xyAgreement.init(key);

                short length = xyAgreement.generateSecret(
                    BASE, (short)0, (short)65,
                    b, (short)0);

                apdu.setOutgoingAndSend((short)0, length);
            } catch (CryptoException e) {
                ISOException.throwIt((short)(
                    0x6F00 | (e.getReason() & 0x0F)));
            }
            return;
        }

        if (b[ISO7816.OFFSET_INS] != (byte)0x71) {
            ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
        }

        byte step = b[ISO7816.OFFSET_P1];

        if (b[ISO7816.OFFSET_P2] != (byte)0) {
            ISOException.throwIt(ISO7816.SW_INCORRECT_P1P2);
        }

        if (step == (byte)0) {
            b[0] = stage;
            apdu.setOutgoingAndSend((short)0, (short)1);
            return;
        }

        if (step != (byte)(stage + 1) || step > (byte)11) {
            ISOException.throwIt(ISO7816.SW_CONDITIONS_NOT_SATISFIED);
        }

        try {
            switch (step) {
                case 1:
                    key = (ECPrivateKey)KeyBuilder.buildKey(
                        KeyBuilder.TYPE_EC_FP_PRIVATE,
                        KeyBuilder.LENGTH_EC_FP_256,
                        false);
                    break;

                case 2:
                    key.setFieldFP(FIELD, (short)0, (short)32);
                    break;

                case 3:
                    key.setA(CURVE_A, (short)0, (short)32);
                    break;

                case 4:
                    key.setB(CURVE_B, (short)0, (short)32);
                    break;

                case 5:
                    key.setG(BASE, (short)0, (short)65);
                    break;

                case 6:
                    key.setR(ORDER, (short)0, (short)32);
                    break;

                case 7:
                    // JCOP4 PACE-GM provider compatibility.
                    // K=1 is not the mathematical curve cofactor (8).
                    key.setK((short)1);
                    break;

                case 8:
                    agreement = KeyAgreement.getInstance(
                        KeyAgreement.ALG_EC_SVDP_DH_PLAIN,
                        false);
                    break;

                case 9:
                    key.setS(TWO, (short)0, (short)32);
                    break;

                case 10:
                    agreement.init(key);
                    break;

                case 11:
                    short length = agreement.generateSecret(
                        BASE, (short)0, (short)65,
                        b, (short)0);
                    stage = step;
                    apdu.setOutgoingAndSend((short)0, length);
                    return;

                default:
                    ISOException.throwIt(
                        ISO7816.SW_INCORRECT_P1P2);
            }

            stage = step;
            b[0] = stage;
            apdu.setOutgoingAndSend((short)0, (short)1);

        } catch (CryptoException e) {
            ISOException.throwIt((short)(
                0x6F00 |
                ((step & 0x0F) << 4) |
                (e.getReason() & 0x0F)
            ));
        } catch (SystemException e) {
            ISOException.throwIt((short)(
                0x6E00 |
                ((step & 0x0F) << 4) |
                (e.getReason() & 0x0F)
            ));
        }
    }
}
