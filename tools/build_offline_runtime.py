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
    min-height:44px!important;padding:8px 5px!important;
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

def replace_once(html, old, new, reason):
    if html.count(old) != 1:
        raise SystemExit("BLOCKED: unexpected historical " + reason + " boundary")
    return html.replace(old, new, 1)


def patch_three_startup_and_picking(html):
    # Keep the classic script global lexical scope and exact render loop.
    # Run it only after the one real renderer instance is successfully created.
    html = replace_once(html, '<script>\nconst codeSample=',
        '<script type="application/x-hs-three-source" id="hsThreeSource">\nconst codeSample=', "Three startup")
    html = replace_once(html,
        'const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true});',
        'const renderer=window.__hsThreeRenderer;delete window.__hsThreeRenderer;', "renderer initialization")
    html = replace_once(html, "requestAnimationFrame(animate);\nlog('3D Lab sẵn sàng.",
        "requestAnimationFrame(animate);\nwindow.__hsThreeReady=true;\nlog('3D Lab sẵn sàng.", "Three readiness")
    html = replace_once(html, "  if(!o)return;\n  let p=o.object;",
        """  if(!o)return;
  const header=pcb.getObjectByName('30-pin header');
  if(o.object===header && Number.isInteger(o.instanceId)){
    const pinId=header.userData.instanceIds[o.instanceId];
    if(typeof pinId==='string'){
      selectedObject=Object.freeze({userData:Object.freeze({pinId,title:'ESP32 · '+pinId,type:'Header pin · REFERENCE_ONLY',node:pinId==='D2'?'D2 / GPIO2 (reference)':pinId+' (reference)'})});
      showInspect(selectedObject);return;
    }
  }
  let p=o.object;""", "pin hit selection")
    html = replace_once(html, "function showInspect(o){\n",
        """function showInspect(o){
  const panel=document.querySelector('.inspector');
  if(o.userData.pinId){
    panel.dataset.pinId=o.userData.pinId;
    document.getElementById('inspectTitle').textContent=o.userData.title;
    document.getElementById('inspectType').textContent=o.userData.type;
    document.getElementById('inspectNode').textContent=o.userData.node;
    document.getElementById('inspectVolt').textContent='UNVERIFIED';
    document.getElementById('inspectState').textContent='UNVERIFIED_CONTACT';
    return;
  }
  delete panel.dataset.pinId;
""", "pin inspector projection")
    return html


def patch_observed_contrast(html, site):
    # FC02 actual Windows Chromium composited measurements, artifact 15044044689.
    # Modify original style owners in generated HTML; no geometry or logic changes.
    palettes = {
        "prototypes/v5_mna_solver": [("#1c9085,#407ce8", "#12675f,#2857a5")],
        "visual/3d_offline_prototype": [("#1b9185,#407de9", "#12675f,#2857a5"), ("#1c9185,#407ce8", "#12675f,#2857a5")],
        "visual/3d_threejs_prototype": [("#1b9185,#407de9", "#12675f,#2857a5"), ("#1c9185,#407ce8", "#12675f,#2857a5")],
        "visual/visual_prototype_1": [("#188f84,#3d7be9", "#12675f,#2857a5")],
    }
    for old, new in palettes[site]:
        html = replace_once(html, old, new, "primary/active contrast")
    if site == "prototypes/v5_mna_solver":
        html = replace_once(html, ".pname{font-size:8px;color:#a9b8cb;min-width:43px}",
            ".pname{font-size:8px;color:#e6f1ff;background:#101c2b;min-width:43px}", "pin name foreground/background")
        html = replace_once(html, "font-size:8px;color:#515963}", 
            "font-size:8px;color:#343e49}.bb-labels span{background:#f3f5f7}", "breadboard row foreground/background")
        # Keep actual wire SVG and every endpoint in place. Only labels participate
        # above that pointer-transparent layer; board bodies remain underneath it.
        html = replace_once(html, "inset 0 0 0 2px #090d12;z-index:18}",
            "inset 0 0 0 2px #090d12;z-index:auto}", "V5 board label stacking context")
        html = replace_once(html, "inset 0 0 20px rgba(0,0,0,.12);z-index:10}",
            "inset 0 0 20px rgba(0,0,0,.12);z-index:auto}", "V5 breadboard label stacking context")
        html = replace_once(html, "color:#e6f1ff;background:#101c2b;min-width:43px}",
            "color:#e6f1ff;background:#101c2b;min-width:43px;position:relative;z-index:21}", "V5 visible pin labels")
        html = replace_once(html, ".bb-labels span{background:#f3f5f7}",
            ".bb-labels span{background:#f3f5f7;position:relative;z-index:21;align-self:start}", "V5 visible row labels")
        html = replace_once(html, "font-size:10px;color:#515963;letter-spacing:1px}",
            "font-size:10px;color:#343e49;background:#f3f5f7;letter-spacing:1px;z-index:21}", "V5 readable board title")
        html = replace_once(html, '.stage{min-height:680px}.breadboard{left:280px}',
            '.stage{min-height:680px;min-width:0;overflow-x:auto}.bench{min-width:780px}.breadboard{left:280px}', "V5 narrow viewport spatial scroll")
        html = replace_once(html, '<div class="stage">', 
            '<div class="stage" tabindex="0" role="region" aria-label="Bàn lab; cuộn ngang để xem toàn bộ breadboard">', "V5 keyboard scroll region")

    elif site == "visual/visual_prototype_1":
        html = replace_once(html, "font-size:7px;color:#838990}",
            "font-size:7px;color:#343e49}.bbnum span{background:#f3f5f7}", "CSS board number foreground/background")
    return html


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
            # Replace only the visual geometry span of the verified historical HTML.
            start = "// ESP32\nconst esp="
            end = "// Current particles"
            if html.count(start) != 1 or html.count(end) != 1:
                raise SystemExit("BLOCKED: historical geometry boundary drift")
            lo = html.index(start)
            hi = html.index(end, lo)
            p1 = (ROOT / "tools" / "hardware_reference_geometry.js").read_text(encoding="utf-8")
            if "</script" in p1.lower():
                raise SystemExit("BLOCKED: invalid P1 visual source")
            html = html[:lo] + p1 + "\n\n" + html[hi:]
            html = patch_three_startup_and_picking(html)
        elif site == "prototypes/v5_mna_solver":
            html = replace_once(html, "font-size:10px;color:#777;letter-spacing:1px",
                "font-size:10px;color:#515963;letter-spacing:1px", "breadboard title contrast")
            html = replace_once(html, "font-size:8px;color:#72777e",
                "font-size:8px;color:#515963", "breadboard row-label contrast")
        elif OLD_CDN in html:
            raise SystemExit("BLOCKED: unexpected remote Three.js dependency in " + site)
        html = patch_observed_contrast(html, site)
        if html.count("</head>") != 1 or html.count("</body>") != 1:
            raise SystemExit("BLOCKED: malformed runtime HTML: " + site)
        html = html.replace("</head>", MOBILE_CSS + "\n</head>")
        camera_kind = {
            "visual/3d_offline_prototype": "canvas",
            "visual/3d_threejs_prototype": "three",
            "visual/visual_prototype_1": "css",
        }.get(site)
        camera_tag = (
            '<script src="../../vendor/keyboard-camera.js" '
            'data-hs-camera-kind="' + camera_kind + '"></script>'
            if camera_kind else ""
        )
        visual_tag = (
            '<script src="../../vendor/visual-framing-labels.js"></script>'
            if site == "visual/3d_threejs_prototype" else ""
        )
        bootstrap_tag = ('<script src="../../vendor/three-runtime-bootstrap.js"></script>'
                         if site == "visual/3d_threejs_prototype" else "")
        html = html.replace("</body>", bootstrap_tag + "\n" + MOBILE_SCRIPT + "\n" + camera_tag + "\n" + visual_tag + "\n</body>")
        (target / "index.html").write_text(html, encoding="utf-8")
        emitted.append(site + "/index.html")
    vendor_dir = DIST / "vendor"
    vendor_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "tools" / "three_runtime_bootstrap.js", vendor_dir / "three-runtime-bootstrap.js")
    shutil.copyfile(ROOT / "tools" / "keyboard_camera.js", vendor_dir / "keyboard-camera.js")
    shutil.copyfile(ROOT / "tools" / "visual_framing_labels.js", vendor_dir / "visual-framing-labels.js")
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
        "keyboardCamera": "vendor/keyboard-camera.js",
        "keyboardCameraKinds": ["canvas", "three", "css"],
        "visualFraming": "vendor/visual-framing-labels.js",
        "threeBootstrap": "vendor/three-runtime-bootstrap.js",
        "hardwareReference": "DOIT_30_PIN_REFERENCE_ONLY",
        "modelProvenance": "hardware-reference-provenance.json",
        "entrypoints": emitted,
    }
    shutil.copyfile(ROOT / "docs" / "hardware-reference-provenance.json", DIST / "hardware-reference-provenance.json")
    (DIST / "runtime-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("LOCAL_RUNTIME_PREPARED", len(emitted), "sourceSHA256", digest)


if __name__ == "__main__":
    main()
