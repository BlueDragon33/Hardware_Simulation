"""Static guard: generated camera keyboard bridge only, historical ZIP unchanged."""
import hashlib
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DIST=ROOT/"runtime_dist"
SOURCE=ROOT/"recovered_prototypes"
ZIP=ROOT/"archive/source_bundle/Hardware_Simulation_All_Prototypes_Source.zip"
SHA="293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f"
KINDS={
    "visual/3d_offline_prototype":"canvas",
    "visual/3d_threejs_prototype":"three",
    "visual/visual_prototype_1":"css",
}

class KeyboardCameraBundle(unittest.TestCase):
    def test_archive_unchanged(self):
        self.assertEqual(hashlib.sha256(ZIP.read_bytes()).hexdigest(),SHA)

    def test_three_generated_entrypoints_and_not_historical(self):
        for path,kind in KINDS.items():
            with self.subTest(path=path):
                original=(SOURCE/path/"index.html").read_text(encoding="utf8")
                output=(DIST/path/"index.html").read_text(encoding="utf8")
                tag='<script src="../../vendor/keyboard-camera.js" data-hs-camera-kind="'+kind+'"></script>'
                self.assertEqual(output.count(tag),1)
                self.assertNotIn("keyboard-camera.js",original)

    def test_firmware_scope_separate(self):
        output=(DIST/"prototypes/v5_mna_solver/index.html").read_text(encoding="utf8")
        self.assertNotIn("keyboard-camera.js",output)

    def test_bridge_and_instructions_bundled(self):
        src=(ROOT/"tools/keyboard_camera.js").read_bytes()
        out=(DIST/"vendor/keyboard-camera.js").read_bytes()
        self.assertEqual(src,out)
        self.assertIn(b'aria-keyshortcuts',out)
        self.assertIn(b'__hsCameraQA',out)

if __name__=="__main__":
    unittest.main()
