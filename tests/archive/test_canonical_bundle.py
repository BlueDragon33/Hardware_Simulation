"""Offline regression: canonical historical snapshot is byte-verified and ZIP-safe."""
import base64
import hashlib
import io
from pathlib import Path
import re
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "archive" / "source_bundle"
EXPECTED = "293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f"
PROTOTYPES = (
    "prototypes/v1_basic/index.html",
    "prototypes/v2_interactive_wiring/index.html",
    "prototypes/v3_sensors/index.html",
    "prototypes/v3_sensors/app.js",
    "prototypes/v3_sensors/style.css",
    "prototypes/v4_breadboard_netlist/index.html",
    "prototypes/v5_mna_solver/index.html",
    "visual/3d_threejs_prototype/index.html",
    "visual/3d_offline_prototype/index.html",
    "visual/visual_prototype_1/index.html",
)


class CanonicalBundle(unittest.TestCase):
    def test_history_is_portable_and_unmodified(self):
        manifest = (BUNDLE / "SHA256SUMS.txt").read_text(encoding="ascii")
        self.assertEqual(manifest.strip(), EXPECTED + "  Hardware_Simulation_All_Prototypes_Source.zip")
        parts = sorted((BUNDLE / "base64").glob("part*.txt"))
        self.assertEqual([p.name for p in parts], [
            "part001.txt", "part002.txt", "part003.txt", "part004.txt",
            "part005.txt", "part006.txt", "part007.txt", "part007b.txt",
            "part008.txt", "part009.txt", "part010.txt", "part011.txt",
            "part012.txt", "part013.txt", "part014.txt", "part015.txt", "part016.txt",
        ])
        payload = base64.b64decode("".join(p.read_text(encoding="ascii").strip() for p in parts), validate=True)
        self.assertEqual(hashlib.sha256(payload).hexdigest(), EXPECTED)
        with zipfile.ZipFile(io.BytesIO(payload)) as z:
            self.assertIsNone(z.testzip(), "CRC error in historical snapshot")
            self.assertEqual(len(z.infolist()), 31)
            files = [p.filename for p in z.infolist() if not p.is_dir()]
            self.assertEqual(len(files), 20)
            for name in files:
                self.assertFalse(name.startswith("/"))
                self.assertNotIn("..", Path(name).parts)
                self.assertIsNone(re.match(r"^[a-zA-Z]:", name))
            self.assertTrue(set(PROTOTYPES).issubset(files))


if __name__ == "__main__":
    unittest.main()
