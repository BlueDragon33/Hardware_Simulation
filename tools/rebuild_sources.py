"""Restore the archived prototype snapshot only if the published checksum matches.

The archive is historical evidence, not a verified production simulator.
"""
from pathlib import Path
import base64
import binascii
import hashlib
import io
import re
import stat
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "archive" / "source_bundle"
PARTS = BUNDLE / "base64"
OUT = BUNDLE / "Hardware_Simulation_All_Prototypes_Source.zip"
EXTRACT_TO = ROOT / "recovered_prototypes"


def restore():
    checksum_file = BUNDLE / "SHA256SUMS.txt"
    rows = checksum_file.read_text(encoding="utf-8").splitlines()
    digests = re.findall(
        r"^([a-fA-F0-9]{64})\s+Hardware_Simulation_All_Prototypes_Source\.zip\s*$",
        "\n".join(rows), re.MULTILINE,
    )
    if len(digests) != 1:
        raise ValueError("Missing or ambiguous expected source-bundle SHA-256")

    parts = sorted(PARTS.glob("part*.txt"))
    if not parts:
        raise ValueError("No source bundle parts found")
    encoded = "".join(p.read_text(encoding="ascii").strip() for p in parts)
    try:
        payload = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Invalid base64 source bundle") from exc

    observed = hashlib.sha256(payload).hexdigest()
    expected = digests[0].lower()
    if observed != expected:
        raise ValueError(f"Archive SHA-256 MISMATCH: expected={expected} actual={observed}")

    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        members = z.infolist()
        for m in members:
            normalized = m.filename.replace("\\", "/")
            if (not normalized or normalized.startswith("/") or
                ".." in Path(normalized).parts or
                re.match(r"^[a-zA-Z]:", normalized) or
                stat.S_IFMT(m.external_attr >> 16) == stat.S_IFLNK):
                raise ValueError(f"Unsafe archive member: {m.filename!r}")
        bad_member = z.testzip()
        if bad_member is not None:
            raise ValueError(f"ZIP CRC validation FAILED: {bad_member}")
        if OUT.exists() and OUT.read_bytes() != payload:
            raise ValueError(f"Existing ZIP differs; refusing overwrite: {OUT}")
        if EXTRACT_TO.exists() and any(EXTRACT_TO.iterdir()):
            raise ValueError(f"Extraction target not empty; refusing overwrite: {EXTRACT_TO}")
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_bytes(payload)
        EXTRACT_TO.mkdir(parents=True, exist_ok=True)
        z.extractall(EXTRACT_TO)
    return observed, len(members)


if __name__ == "__main__":
    try:
        digest, count = restore()
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        raise SystemExit(f"BLOCKED: {exc}") from exc
    print(f"RESTORED: {OUT}")
    print(f"SHA256 VERIFIED: {digest} / ZIP entries: {count}")
    print(f"EXTRACTED: {EXTRACT_TO}")
