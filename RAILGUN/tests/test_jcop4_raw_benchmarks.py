"""Integrity tests for externally supplied JCOP4 physical benchmark reports.

No card access, no network, no simulated physical data.
"""
import hashlib
import json
from pathlib import Path
import statistics
import unittest

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'benchmarks/jcop4-2026-11-19/raw'
HASHES = {
    'JCOP4-algoprobe-2026-11-19.json': '2c29c5dc520a8962cb173393319e0f7acd8bb0d249a24fe398e79bb1f772a0b6',
    'JCOP4-native-ec-2026-11-19.json': '5ec9f747fbf1a034e20e37543aaa47b192adb43064dba090d6fc87de036c8944',
    'JCOP4-pace-gm-2026-11-19.json': '7f2275332bbb5f73ce993a6ac787b613d987d194b9403cb30a3eb6e43e22eae5',
    'JCOP4-pace-k1-2026-11-19.json': 'a4ee96954f95a0fc8ea3d30a56f9d26bfb43a0fcb34eaceb034ee272b76acaef',
}

class Evidence(unittest.TestCase):
    def load(self, name):
        return json.loads((DIR / name).read_text())

    def test_pinned_bytes(self):
        for name, expected in HASHES.items():
            with self.subTest(name=name):
                p=DIR/name
                self.assertFalse(p.is_symlink())
                self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),expected)

    def test_k1_all_50_physical_samples(self):
        k=self.load('JCOP4-pace-k1-2026-11-19.json')
        self.assertEqual((k['status'],k['applet_aid']),('PASS','F0424E3235344D01'))
        samples=[x for row in k['rounds_detail'] for x in row]
        self.assertEqual(len(samples),50)
        self.assertEqual(k['exact_matches'],50)
        self.assertTrue(all(x['status_word']=='9000' and x['response_match'] for x in samples))
        self.assertAlmostEqual(statistics.median(x['transmit_ms'] for x in samples),k['median_transmit_ms'],places=3)
        self.assertEqual(k['variant_cap_sha256'],'4e50bcd2092e8d5feaef36420016dbfa044465b55f7671380852040b737c0efc')

    def test_original_applet_failures(self):
        n=self.load('JCOP4-native-ec-2026-11-19.json')
        p=self.load('JCOP4-pace-gm-2026-11-19.json')
        self.assertEqual((n['status'],n['operations_verified'],n['operations_total']),('PARTIAL',11,18))
        self.assertEqual((p['status'],p['operations_verified'],p['operations_total']),('PARTIAL',13,30))
        self.assertEqual(n['operations']['xy_wide_0']['status_words'],{'6F02':10})
        self.assertEqual(p['operations']['pace_add_0']['status_words'],{'6F02':10})
        self.assertEqual(n['operations']['plain_wide_5']['median_ms'],85.706)
        self.assertEqual(p['operations']['rsa_cube_1024']['median_ms'],241.751)

    def test_algoprobe_cofactor_fix(self):
        a=self.load('JCOP4-algoprobe-2026-11-19.json')
        missing=[e for e in a['experiments'] if e['variant']==0 and e['algorithm'] in (5,6)]
        fixed=[e for e in a['experiments'] if e['variant']==4 and e['algorithm'] in (5,6)]
        self.assertEqual(len(missing),2)
        self.assertTrue(all(e['outcome']=='failure' for e in missing))
        self.assertEqual(len(fixed),2)
        self.assertTrue(all(e['outcome']=='success' for e in fixed))
        self.assertEqual({e['expected_match'] for e in fixed},{'04||3G','04||2G'})

    def test_no_wallet_operations_in_reports(self):
        for name in HASHES:
            x=self.load(name)
            self.assertIs(x['wallet_signing'],False)
            self.assertIs(x['installation'],False)

if __name__=='__main__':
    unittest.main()
