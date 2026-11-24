"""Build a local, offline-capable runtime from the immutable verified source archive.

The historical archived HTML and ZIP bytes are NEVER modified. This emits a
separate generated runtime tree. A bundled Three.js IIFE is added by the Node
build step, not downloaded by the browser at runtime.
"""
from pathlib import Path
import hashlib
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "recovered_prototypes"
DIST = ROOT / "runtime_dist"
ZIP = ROOT / "archive/source_bundle/Hardware_Simulation_All_Prototypes_Source.zip"
EXPECTED_SHA = "293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f"
SITES = (
    "prototypes/v5_mna_solver",
    "visual/3d_offline_prototype",
    "visual/3d_threejs_prototype",
    "visual/visual_prototype_1",
)
OLD_CDN = "https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.min.js"
NEW_BUNDLE = "../../vendor/three-runtime.iife.js"
GENERATED_MARK = ".hs-g0-generated-runtime"

MOBILE_CSS = """
<style id="hs-g0-mobile-overlay-remediation">
@media (max-width: 600px) {
  .viewport .overlay, .viewport > .toolbar {
    position:absolute!important;left:8px!important;right:8px!important;
    top:8px!important;bottom:auto!important;z-index:55!important;
    display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:6px!important;width:auto!important;
  }
  .viewport .overlay button, .viewport > .toolbar button {
    display:block!important;width:100%!important;min-width:0!important;
    min-height:39px!important;padding:8px 5px!important;
    font-size:10px!important;white-space:normal!important;
  }
  .viewport {height:70svh!important;min-height:560px!important}
  .hud {left:8px!important;right:8px!important;bottom:8px!important;
    grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:5px!important}
  .hud .card {min-width:0!important;padding:6px 8px!important}
  .hud .card:nth-child(n+3) {display:none!important}
  .scene-wrap {transform:translate(-50%,-50%) scale(.7)!important}
  .side {height:auto!important;min-height:760px!important;overflow:visible!important;
    grid-template-rows:48px minmax(250px,1fr) auto auto!important}
  .side > .tip, .side > .inspector, .side > .help, .side > .inspect {
    position:static!important;transform:none!important;display:block!important;
    width:auto!important;height:auto!important;max-width:none!important;
    margin:8px 12px!important;inset:auto!important;z-index:auto!important;
    pointer-events:auto!important;
  }
}
</style>
"""
MOBILE_SCRIPT = """
<script id="hs-g0-mobile-overlay-layout">
(function () {
  'use strict';
  const scene = document.querySelector('.viewport');
  const side = document.querySelector('.side');
  if (!scene || !side) return;
  const overlays = Array.from(scene.querySelectorAll('.tip,.inspector,.help,.inspect'));
  const original = overlays.map(element => ({
    element, parent: element.parentNode, next: element.nextSibling
  }));
  function update() {
    const small = window.matchMedia('(max-width: 600px)').matches;
    for (const slot of original) {
      if (small) {
        if (slot.element.parentNode !== side) side.appendChild(slot.element);
      } else if (slot.element.parentNode !== slot.parent) {
        if (slot.next && slot.next.parentNode === slot.parent) {
          slot.parent.insertBefore(slot.element, slot.next);
        } else {
          slot.parent.appendChild(slot.element);
        }
      }
    }
    document.documentElement.dataset.hsMobileLayout = small ? 'side-inspector' : 'desktop-inspector';
  }
  window.addEventListener('resize', update, {passive:true});
  update();
})();
</script>
"""

def main():
    if not ZIP.exists():
        raise SystemExit("BLOCKED: rebuild_sources.py must restore pinned ZIP first")
    digest = hashlib.sha256(ZIP.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA:
        raise SystemExit("BLOCKED: source ZIP SHA mismatch: " + digest)
    for site in SITES:
        if not (SOURCE / site / "index.html").is_file():
            raise SystemExit("BLOCKED: missing verified source entry: " + site)
    if DIST.exists():
        marker = DIST / GENERATED_MARK
        if not marker.is_file() or marker.read_text(encoding="utf-8") != EXPECTED_SHA:
            raise SystemExit("BLOCKED: runtime_dist exists without matching generated marker")
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    (DIST / GENERATED_MARK).write_text(EXPECTED_SHA, encoding="utf-8")
    emitted = []
    for site in SITES:
        target = DIST / site
        shutil.copytree(SOURCE / site, target)
        html = (target / "index.html").read_text(encoding="utf-8")
        if site == "visual/3d_threejs_prototype":
            if html.count(OLD_CDN) != 1:
                raise SystemExit("BLOCKED: unexpected legacy Three.js dependency reference")
            html = html.replace(OLD_CDN, NEW_BUNDLE)
        elif OLD_CDN in html:
            raise SystemExit("BLOCKED: unexpected remote Three.js dependency in " + site)
        if html.count("</head>") != 1 or html.count("</body>") != 1:
            raise SystemExit("BLOCKED: malformed runtime HTML: " + site)
        html = html.replace("</head>", MOBILE_CSS + "\n</head>")
        html = html.replace("</body>", MOBILE_SCRIPT + "\n</body>")
        (target / "index.html").write_text(html, encoding="utf-8")
        emitted.append(site + "/index.html")
    (DIST / "index.html").write_text(
        '<!doctype html><html lang="vi"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Hardware Simulation — Offline QA</title>'
        '<style>body{font:16px system-ui;background:#07101c;color:#e8f5ff;padding:2rem}'
        'a{display:block;color:#58bbff;padding:1rem}</style>'
        '<h1>Hardware Simulation — Local Runtime</h1>'
        '<p>Đây là các prototype lịch sử được đóng gói để QA offline, chưa phải bản nghiệm thu.</p>'
        + "".join('<a href="./' + s + '">' + s + '</a>' for s in emitted)
        + '</html>', encoding="utf-8")
    manifest = {
        "schema": "hs.g0.local-runtime.v1",
        "historicalSourceSha256": digest,
        "threeVersion": "0.161.0",
        "bundle": "vendor/three-runtime.iife.js",
        "offlineRuntimeAfterBuild": True,
        "historicalArchiveUnchanged": True,
        "entrypoints": emitted,
    }
    (DIST / "runtime-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("LOCAL_RUNTIME_PREPARED", len(emitted), "sourceSHA256", digest)


if __name__ == "__main__":
    main()
