"""Stdlib-only fail-closed regression tests for the prototype archive restorer."""
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import base64
import subprocess
import sys
import unittest
import zipfile

SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "rebuild_sources.py"


def zip_bytes(name="sample/hello.txt"):
    f = BytesIO()
    with zipfile.ZipFile(f, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(name, "sample content")
    return f.getvalue()


class ArchiveRestoration(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tool = self.root / "tools"
        self.bundle = self.root / "archive" / "source_bundle"
        self.parts = self.bundle / "base64"
        self.tool.mkdir(parents=True)
        self.parts.mkdir(parents=True)
        (self.tool / "rebuild_sources.py").write_bytes(SCRIPT.read_bytes())

    def prepare(self, payload, expected=None):
        encoded = base64.b64encode(payload).decode("ascii")
        midpoint = len(encoded) // 2
        (self.parts / "part001.txt").write_text(encoded[:midpoint])
        (self.parts / "part002.txt").write_text(encoded[midpoint:])
        (self.bundle / "SHA256SUMS.txt").write_text(
            (expected or sha256(payload).hexdigest()) + "  Hardware_Simulation_All_Prototypes_Source.zip\n"
        )

    def run_restorer(self):
        return subprocess.run(
            [sys.executable, str(self.tool / "rebuild_sources.py")],
            cwd=self.root, capture_output=True, text=True, timeout=10,
        )

    def test_valid_archive_restores_and_checksum_matches(self):
        data = zip_bytes()
        self.prepare(data)
        p = self.run_restorer()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("SHA256 VERIFIED", p.stdout)
        self.assertEqual((self.root / "recovered_prototypes/sample/hello.txt").read_text(), "sample content")

    def test_manifest_mismatch_fails_without_side_effects(self):
        data = zip_bytes()
        self.prepare(data, "0" * 64)
        p = self.run_restorer()
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("SHA-256 MISMATCH", p.stderr)
        self.assertFalse((self.bundle / "Hardware_Simulation_All_Prototypes_Source.zip").exists())
        self.assertFalse((self.root / "recovered_prototypes").exists())

    def test_invalid_base64_fails_closed(self):
        self.prepare(zip_bytes())
        (self.parts / "part002.txt").write_text("!!!")
        p = self.run_restorer()
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("Invalid base64", p.stderr)

    def test_unsafe_archive_member_rejected(self):
        self.prepare(zip_bytes("../escape.txt"))
        p = self.run_restorer()
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("Unsafe archive member", p.stderr)
        self.assertFalse((self.root / "recovered_prototypes").exists())

    def test_nonempty_target_not_overwritten(self):
        data = zip_bytes()
        self.prepare(data)
        target = self.root / "recovered_prototypes"
        target.mkdir()
        (target / "keep.txt").write_text("important")
        p = self.run_restorer()
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("Extraction target not empty", p.stderr)
        self.assertEqual((target / "keep.txt").read_text(), "important")

    def test_exact_nonempty_restore_is_idempotent(self):
        self.prepare(zip_bytes())
        first = self.run_restorer()
        self.assertEqual(first.returncode, 0, first.stderr)
        target = self.root / "recovered_prototypes/sample/hello.txt"
        stamp = target.stat().st_mtime_ns
        second = self.run_restorer()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("REUSED: exact verified extraction", second.stdout)
        self.assertEqual(target.stat().st_mtime_ns, stamp)
        self.assertEqual(target.read_text(), "sample content")

    def test_edited_extraction_rejected_without_overwrite(self):
        self.prepare(zip_bytes())
        self.assertEqual(self.run_restorer().returncode, 0)
        target = self.root / "recovered_prototypes/sample/hello.txt"
        target.write_text("edited content")
        result = self.run_restorer()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing overwrite", result.stderr)
        self.assertEqual(target.read_text(), "edited content")

    def test_missing_extracted_file_rejected_without_repair(self):
        self.prepare(zip_bytes())
        self.assertEqual(self.run_restorer().returncode, 0)
        target = self.root / "recovered_prototypes/sample/hello.txt"
        target.unlink()
        result = self.run_restorer()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(target.exists())

    def test_extra_extracted_file_rejected_without_deletion(self):
        self.prepare(zip_bytes())
        self.assertEqual(self.run_restorer().returncode, 0)
        target = self.root / "recovered_prototypes/sample/extra.txt"
        target.write_text("preserve me")
        result = self.run_restorer()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_text(), "preserve me")


if __name__ == "__main__":
    unittest.main()
