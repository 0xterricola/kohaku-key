"""Offline integrity tests for the JCOP4 PACE-GM K=1 variant.

These tests do not prove physical provider compatibility.
"""

import difflib
import hashlib
import struct
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "RAILGUN"

ORIGINAL = ROOT / "applets/pace-gm"
VARIANT = (
    ROOT / "experiments/physical-benchmark-runner"
    / "applets/pace-gm-k1"
)

JAVA_PATH = (
    "src/main/java/im/status/keycard/railgun/"
    "nativeecprobe/NativeEcProbeApplet.java"
)

ORIGINAL_CAP_HASH = (
    "12083cee1614ad080a24c5af7c3e9b1cdf1aeaedfb67a5fcff22cf97fb4353d8"
)

VARIANT_COMPONENT_HASH = (
    "a5dfbcd5b875c1a8d539ac480fea98017808d4c2b34f94b13c043d7dbbaa1e96"
)

ORIGINAL_STAGE = (
    "case 7:\n"
    "                    // Plain ECDH does not require "
    "the cofactor to be set.\n"
    "                    break;"
)

VARIANT_STAGE = (
    "case 7:\n"
    "                    // JCOP4 PACE-GM provider compatibility.\n"
    "                    // K=1 is not the mathematical curve cofactor (8).\n"
    "                    key.setK((short)1);\n"
    "                    break;"
)


def check_source_pair(original, variant):
    """Reject unexpected source changes or K initialization changes."""
    if original.count(ORIGINAL_STAGE) != 1:
        raise ValueError("Published step 7 changed")

    if variant.count(VARIANT_STAGE) != 1:
        raise ValueError("JCOP4 step 7 changed")

    if "key.setK(" in original:
        raise ValueError("Published applet contains setK")

    if variant.count("key.setK(") != 1:
        raise ValueError("Unexpected setK usage")

    expected = original.replace(
        ORIGINAL_STAGE, VARIANT_STAGE, 1
    )

    if variant != expected:
        raise ValueError("Unexpected Java source difference")


def component_digest(cap):
    """Hash named uncompressed CAP components in stable order."""
    digest = hashlib.sha256()

    with zipfile.ZipFile(cap) as archive:
        names = sorted(
            name for name in archive.namelist()
            if name.endswith(".cap")
        )

        if len(names) != 10:
            raise ValueError("Unexpected CAP component count")

        for name in names:
            data = archive.read(name)
            encoded = name.encode("utf-8")
            digest.update(struct.pack(">I", len(encoded)))
            digest.update(encoded)
            digest.update(struct.pack(">Q", len(data)))
            digest.update(data)

        header = archive.read(next(
            name for name in names
            if name.endswith("/Header.cap")
        ))
        applet = archive.read(next(
            name for name in names
            if name.endswith("/Applet.cap")
        ))

        package_aid = header[
            13:13 + header[12]
        ].hex().upper()

        applet_aid = applet[
            5:5 + applet[4]
        ].hex().upper()

        if package_aid != "F0424E3235344E00":
            raise ValueError("Unexpected variant package AID")

        if applet_aid != "F0424E3235344E01":
            raise ValueError("Unexpected variant applet AID")

    return digest.hexdigest()


class PaceCofactorTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.original = (ORIGINAL / JAVA_PATH).read_text()
        cls.variant = (VARIANT / JAVA_PATH).read_text()

    def test_01_exact_isolated_source_change(self):
        check_source_pair(self.original, self.variant)

    def test_02_reject_incorrect_k8(self):
        altered = self.variant.replace(
            "key.setK((short)1);",
            "key.setK((short)8);"
        )
        with self.assertRaises(ValueError):
            check_source_pair(self.original, altered)

    def test_03_reject_missing_cofactor(self):
        altered = self.variant.replace(
            "key.setK((short)1);", ""
        )
        with self.assertRaises(ValueError):
            check_source_pair(self.original, altered)

    def test_04_reject_misplaced_cofactor(self):
        altered = self.variant.replace(
            "key.setK((short)1);",
            ""
        ).replace(
            "case 8:",
            "key.setK((short)1);\n                case 8:",
            1
        )
        with self.assertRaises(ValueError):
            check_source_pair(self.original, altered)

    def test_05_reject_other_source_changes(self):
        altered = self.variant.replace(
            "case 8:", "case 9:", 1
        )
        with self.assertRaises(ValueError):
            check_source_pair(self.original, altered)

    def test_06_published_cap_unchanged(self):
        cap = ORIGINAL / "pace-gm.cap"
        actual = hashlib.sha256(cap.read_bytes()).hexdigest()
        self.assertEqual(actual, ORIGINAL_CAP_HASH)

    def test_07_variant_cap_components(self):
        cap = VARIANT / "pace-gm-k1.cap"
        self.assertEqual(
            component_digest(cap),
            VARIANT_COMPONENT_HASH
        )

    def test_08_documented_provider_boundary(self):
        doc = (
            VARIANT / "JCOP4-COMPATIBILITY.md"
        ).read_text()

        self.assertIn("key.setK((short)1)", doc)
        self.assertIn("cofactor", doc.lower())
        self.assertIn("8", doc)
        self.assertIn("50/50", doc)
        self.assertIn("unverified", doc.lower())


if __name__ == "__main__":
    unittest.main()
