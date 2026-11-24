"""HS-G0-001 acceptance probe: new Chromium contexts with isolated local HTTP only.

A PASS of these scoped probes is NOT G0 product acceptance, a visual quality PASS,
an air-gapped OS test, or a claim of firmware/numerical correctness.
"""
from __future__ import annotations

import hashlib
import http.server
import json
import platform
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"runtime_dist"
OUTPUT=ROOT/"tests"/"acceptance_output"
CASES=(
    "prototypes/v5_mna_solver/index.html",
    "visual/3d_offline_prototype/index.html",
    "visual/3d_threejs_prototype/index.html",
    "visual/visual_prototype_1/index.html",
)
SIZES=((1440,900),(800,900),(390,844))
PINNED="293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(SOURCE),**kwargs)
    def log_message(self,*args):
        return


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    result={
        "schema":"hardware-simulation.hs-g0-001.acceptance-v1",
        "timestamp":datetime.now(timezone.utc).isoformat(),
        "runner":platform.platform(),
        "source_sha256":PINNED,
        "network_isolation":"Playwright route aborts every request outside loopback; NOT physical OS airgap",
        "cold_start":"new incognito browser context and page for every viewport; initial navigation and reload",
        "gate":"BLOCKED_PENDING_ACTUAL_EVIDENCE",
        "cases":[],
        "scope":"evidence-only; no G1 or Product PASS",
    }
    server=None
    try:
        bundle=SOURCE/"vendor"/"three-runtime.iife.js"
        manifest=json.loads((SOURCE/"runtime-manifest.json").read_text(encoding="utf-8"))
        assert manifest["historicalSourceSha256"]==PINNED
        assert manifest["threeVersion"]=="0.161.0"
        result["vendor_sha256"]=sha(bundle.read_bytes())
        result["vendor_size"]=bundle.stat().st_size
        result["input_source_zip_sha256"]=sha((ROOT/"archive"/"source_bundle"/"Hardware_Simulation_All_Prototypes_Source.zip").read_bytes())
        assert result["input_source_zip_sha256"]==PINNED
        server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        origin=f"http://127.0.0.1:{server.server_address[1]}"
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            result["chromium_version"]=browser.version
            for source in CASES:
                for width,height in SIZES:
                    case={
                        "source":source,"viewport":[width,height],
                        "initial":"NOT_RUN","reload":"NOT_RUN","errors":[],
                        "external_requests_blocked":[],"local_request_failures":[],
                        "keyboard_enter":"NOT_VERIFIED","keyboard_camera":"NOT_VERIFIED",
                        "camera_pointer":"NOT_VERIFIED","screenshot_kind":"NONE",
                    }
                    context=browser.new_context(
                        viewport={"width":width,"height":height},
                        device_scale_factor=1,
                        service_workers="block",
                        storage_state={"cookies":[],"origins":[]},
                    )
                    page=context.new_page()
                    page.on("pageerror",lambda err:case["errors"].append(str(err)))
                    def route_handler(route):
                        url=route.request.url
                        if url.startswith(origin+"/"):
                            route.continue_()
                        else:
                            case["external_requests_blocked"].append(url)
                            route.abort()
                    context.route("**/*",route_handler)
                    page.on("requestfailed",lambda req:case["local_request_failures"].append(req.url) if req.url.startswith(origin+"/") else None)
                    try:
                        response=page.goto(origin+"/"+source,wait_until="domcontentloaded",timeout=15000)
                        case["initial"]=response.status if response else None
                        page.wait_for_timeout(350)
                        first_title=page.title()
                        page.reload(wait_until="domcontentloaded",timeout=15000)
                        page.wait_for_timeout(400)
                        case["reload"]=page.title()==first_title and page.locator("body").count()==1
                        if source.startswith("visual/"):
                            case["responsive_inspector_location"]=page.evaluate(
                                "() => document.documentElement.dataset.hsMobileLayout")
                            assert case["responsive_inspector_location"]==(
                                "side-inspector" if width<=600 else "desktop-inspector")
                        if source=="visual/3d_threejs_prototype/index.html":
                            case["three_loaded"]=page.evaluate(
                                "() => typeof THREE==='object' && typeof THREE.WebGLRenderer==='function'")
                            case["canvas_dimensions"]=page.evaluate(
                                "() => {const x=document.querySelector('#gl');return x?[x.width,x.height]:null}")
                            btn=page.locator("#btnEngineer")
                            btn.focus()
                            page.keyboard.press("Enter")
                            case["keyboard_enter"]=bool(btn.evaluate("(x)=>x.classList.contains('active')"))
                            # Native scene does not expose a keyboard camera contract yet.
                            gl=page.locator("#gl")
                            case["keyboard_camera"]="FOCUSABLE" if gl.get_attribute("tabindex") is not None else "MISSING_CANVAS_TABINDEX"
                            before=page.screenshot()
                            rect=gl.bounding_box()
                            if rect:
                                x,y=rect["x"]+rect["width"]*.36,rect["y"]+rect["height"]*.48
                                page.mouse.move(x,y)
                                page.mouse.down()
                                page.mouse.move(x+65,y+26,steps=8)
                                page.mouse.up()
                                page.mouse.wheel(0,-160)
                            page.wait_for_timeout(250)
                            case["camera_pointer"]="SCREENSHOT_CHANGED" if sha(before)!=sha(page.screenshot()) else "NOT_OBSERVED"
                        elif source=="visual/3d_offline_prototype/index.html":
                            btn=page.locator("#btnEngineer")
                            btn.focus()
                            page.keyboard.press("Enter")
                            case["keyboard_enter"]=bool(btn.evaluate("(x)=>x.classList.contains('active')"))
                            gl=page.locator("canvas").first
                            case["keyboard_camera"]="FOCUSABLE" if gl.get_attribute("tabindex") is not None else "MISSING_CANVAS_TABINDEX"
                        elif source=="visual/visual_prototype_1/index.html":
                            btn=page.locator("#engineering")
                            btn.focus()
                            page.keyboard.press("Enter")
                            case["keyboard_enter"]=bool(btn.evaluate("(x)=>x.classList.contains('active')"))
                            case["keyboard_camera"]="NO_NATIVE_KEYBOARD_CAMERA_LISTENER"
                        else:
                            run=page.locator("#run")
                            run.focus()
                            page.keyboard.press("Enter")
                            page.wait_for_timeout(750)
                            case["keyboard_enter"]=page.locator("#state").inner_text().endswith("RUNNING")
                        name=source.replace("/","_").replace(".html","")+f"_{width}x{height}.png"
                        page.screenshot(path=str(OUTPUT/name),timeout=10000)
                        case["screenshot"]=name
                        case["screenshot_kind"]="ACTUAL_APPLICATION"
                        case["status"]=("SMOKE_OBSERVED" if case["initial"]==200 and case["reload"]
                                        and not case["errors"] and not case["external_requests_blocked"]
                                        and not case["local_request_failures"] and case["keyboard_enter"]==True
                                        else "BLOCKED_OR_FAILED")
                    except Exception as e:
                        case["status"]="BLOCKED_OR_FAILED"
                        case["exception"]=str(e)[:2000]
                        case["traceback"]=traceback.format_exc(limit=2)
                        try:
                            name="error_"+source.replace("/","_")+f"_{width}x{height}.png"
                            page.screenshot(path=str(OUTPUT/name),timeout=4000)
                            case["diagnostic_screenshot"]=name
                        except Exception:
                            pass
                    finally:
                        result["cases"].append(case)
                        print("CASE",source,width,height,case["status"],case.get("keyboard_camera"),flush=True)
                        context.close()
            browser.close()
        result["smoke_observed"]=sum(c["status"]=="SMOKE_OBSERVED" for c in result["cases"])
        result["keyboard_camera_missing"]=sum("MISSING" in str(c.get("keyboard_camera")) or
                                              "NO_NATIVE" in str(c.get("keyboard_camera")) for c in result["cases"])
        result["gate"]="BLOCKED_PENDING_OWNER_VISUAL_AND_KEYBOARD_ACCEPTANCE"
    except Exception as e:
        result["gate"]="BLOCKED_PRECHECK_OR_QA_ENVIRONMENT"
        result["exception"]=repr(e)
    finally:
        if server:
            server.shutdown()
            server.server_close()
        (OUTPUT/"acceptance_report.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
        print("FINAL_GATE",result["gate"],"SMOKE",result.get("smoke_observed",0),
              "KEYBOARD_MISSING",result.get("keyboard_camera_missing","unknown"),flush=True)
    # Evidence collection is a successful job even if a product gate is BLOCKED.
    # Status lives in report, not in CI job's green check.
    return 0 if "cases" in result and len(result["cases"])==12 else 2


if __name__=="__main__":
    raise SystemExit(main())
