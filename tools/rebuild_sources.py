from pathlib import Path
import base64
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "archive" / "source_bundle" / "base64"
OUT = ROOT / "archive" / "source_bundle" / "Hardware_Simulation_All_Prototypes_Source.zip"
EXTRACT_TO = ROOT / "recovered_prototypes"

parts = sorted(PARTS.glob("part*.txt"))
if not parts:
    raise SystemExit("No source bundle parts found")

payload = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_bytes(base64.b64decode(payload))

EXTRACT_TO.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(OUT) as z:
    z.extractall(EXTRACT_TO)

print(f"Rebuilt: {OUT}")
print(f"Extracted: {EXTRACT_TO}")
