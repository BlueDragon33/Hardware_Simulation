"""Regression assertions on the actually built offline runtime, not its draft."""
from pathlib import Path
import hashlib
import json
import unittest

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runtime_dist"
ZIP = ROOT / "archive" / "source_bundle" / "Hardware_Simulation_All_Prototypes_Source.zip"
EXPECTED = "293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f"
SITES = [
    "prototypes/v5_mna_solver",
    "visual/3d_offline_prototype",
    "visual/3d_threejs_prototype",
    "visual/visual_prototype_1",
]


class OfflineRuntime(unittest.TestCase):
    def test_historical_source_digest_unchanged(self):
        self.assertTrue(ZIP.is_file())
        self.assertEqual(hashlib.sha256(ZIP.read_bytes()).hexdigest(), EXPECTED)
        self.assertEqual((OUT / ".hs-g0-generated-runtime").read_text(encoding="utf-8"), EXPECTED)

    def test_four_local_entrypoints_and_no_remote_three_dependency(self):
        for site in SITES:
            with self.subTest(site=site):
                html = (OUT / site / "index.html").read_text(encoding="utf-8")
                self.assertNotIn("https://cdn.jsdelivr.net", html)
                self.assertIn("hs-g0-mobile-overlay-remediation", html)
                self.assertIn("hs-g0-mobile-overlay-layout", html)
                self.assertIn("side-inspector", html)
                if site == "visual/visual_prototype_1":
                    self.assertIn('id="engineering"', html)
                    self.assertIn("scene-wrap", html)
                else:
                    self.assertIn("<canvas", html)

    def test_bundled_three_and_license_local(self):
        html = (OUT / "visual/3d_threejs_prototype/index.html").read_text(encoding="utf-8")
        self.assertIn("../../vendor/three-runtime.iife.js", html)
        bundle = OUT / "vendor" / "three-runtime.iife.js"
        self.assertGreater(bundle.stat().st_size, 200_000)
        self.assertTrue((OUT / "vendor" / "THREE-LICENSE.txt").is_file())
        data = json.loads((OUT / "runtime-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(data["threeVersion"], "0.161.0")
        self.assertEqual(data["historicalSourceSha256"], EXPECTED)
        self.assertEqual(len(data["entrypoints"]), 4)

    def test_unmodified_historical_html(self):
        # The original archive and its reconstructed source remain separate from build output.
        for site in SITES:
            historical = (ROOT / "recovered_prototypes" / site / "index.html").read_bytes()
            built = (OUT / site / "index.html").read_bytes()
            self.assertNotEqual(historical, built)
        old = (ROOT / "recovered_prototypes" /
               "visual/3d_threejs_prototype/index.html").read_text(encoding="utf-8")
        self.assertIn("https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.min.js", old)


if __name__ == "__main__":
    unittest.main()
