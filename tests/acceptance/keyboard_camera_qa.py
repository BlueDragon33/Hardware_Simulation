"""G0 Windows Chromium evidence for REAL keyboard/pointer camera state, 3 views x 3 sizes."""
import hashlib
import http.server
import json
import threading
import platform
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
DIST=ROOT/"runtime_dist"
OUT=ROOT/"tests"/"camera_output"
SITES=(
    ("visual/3d_offline_prototype/index.html","canvas","#btnEngineer"),
    ("visual/3d_threejs_prototype/index.html","three","#btnEngineer"),
    ("visual/visual_prototype_1/index.html","css","#engineering"),
)
SIZES=((1440,900),(800,900),(390,844))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**k):
        super().__init__(*a,directory=str(DIST),**k)
    def log_message(self,*a):
        pass

def state(page):
    return page.evaluate("() => window.__hsCameraQA.getState()")

def changed(a,b,key):
    return abs(a[key]-b[key]) > 0.00001

def match(a,b):
    return all(abs(a[key]-b[key]) < 0.00001 for key in a)

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    report={"schema":"HS-G0-001.keyboard-camera.qa.v1","runner":platform.platform(),
            "timestamp":datetime.now(timezone.utc).isoformat(),"cases":[],
            "gate":"BLOCKED_NOT_TESTED","isolation":"all non-loopback browser requests aborted"}
    server=None
    try:
        assert (DIST/"vendor"/"keyboard-camera.js").is_file()
        assert (DIST/"vendor"/"three-runtime.iife.js").is_file()
        manifest=json.loads((DIST/"runtime-manifest.json").read_text(encoding="utf8"))
        assert manifest["historicalSourceSha256"]=="293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f"
        assert manifest["keyboardCamera"]=="vendor/keyboard-camera.js"
        server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        origin="http://127.0.0.1:"+str(server.server_address[1])
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            report["browser"]=browser.version
            for source,kind,button in SITES:
                for width,height in SIZES:
                    case={"source":source,"kind":kind,"viewport":[width,height],"status":"NOT_TESTED",
                          "page_errors":[],"external":[],"request_failed":[]}
                    ctx=browser.new_context(viewport={"width":width,"height":height},
                        device_scale_factor=1,service_workers="block",
                        storage_state={"cookies":[],"origins":[]})
                    page=ctx.new_page()
                    page.on("pageerror",lambda e:case["page_errors"].append(str(e)))
                    def route(r):
                        if r.request.url.startswith(origin+"/"):r.continue_()
                        else:
                            case["external"].append(r.request.url)
                            r.abort()
                    ctx.route("**/*",route)
                    page.on("requestfailed",lambda q:case["request_failed"].append(q.url)
                            if q.url.startswith(origin+"/") else None)
                    surface=page.locator("#viewport" if kind=="css" else "#gl")
                    try:
                        response=page.goto(origin+"/"+source,wait_until="domcontentloaded",timeout=18000)
                        assert response is not None and response.status==200
                        page.wait_for_function("() => !!window.__hsCameraQA",timeout=10000)
                        case["focusable"]=surface.get_attribute("tabindex")=="0"
                        assert case["focusable"]
                        assert page.locator("#hsCameraKeyboardStatus").count()==1
                        assert page.evaluate("() => window.__hsCameraQA.kind")==kind
                        page.locator(button).focus()
                        page.keyboard.press("Enter")
                        case["engineering_enter"]=True

                        # Tab must reach the camera; no synthetic key dispatch or direct focus.
                        page.evaluate("() => document.activeElement.blur()")
                        for tries in range(30):
                            page.keyboard.press("Tab")
                            if surface.evaluate("(e) => document.activeElement === e"):
                                case["tab_steps"]=tries+1
                                break
                        assert case.get("tab_steps"),"Camera not reachable by Tab"
                        assert page.evaluate("() => window.__hsCameraQA.focused()")
                        case["focus_status"]=page.locator("#hsCameraKeyboardStatus").inner_text()
                        assert "đang điều khiển" in case["focus_status"]
                        initial=state(page)
                        orbit_key="rz" if kind=="css" else "yaw"
                        pan_key="panY" if kind=="css" else "y"
                        zoom_key="scale" if kind=="css" else "dist"

                        page.keyboard.press("ArrowRight")
                        orbit=state(page)
                        assert changed(orbit,initial,orbit_key),"ArrowRight no orbit"
                        page.keyboard.press("Shift+ArrowUp")
                        pan=state(page)
                        assert changed(pan,orbit,pan_key),"Shift+ArrowUp no pan"
                        page.keyboard.press("Equal")
                        zoom=state(page)
                        assert changed(zoom,pan,zoom_key), "Equal no zoom in"
                        page.keyboard.press("Minus")
                        zoomout=state(page)
                        assert changed(zoomout,zoom,zoom_key), "Minus no zoom out"
                        case["keys"]={"initial":initial,"orbit":orbit,"pan":pan,
                                      "zoom_in":zoom,"zoom_out":zoomout}
                        case["keyboard_moves"]=page.evaluate("() => window.__hsCameraQA.keyboardMoves()")
                        assert case["keyboard_moves"]>=4
                        shot="keyboard_"+kind+"_"+str(width)+"x"+str(height)+".png"
                        page.screenshot(path=str(OUT/shot),timeout=9000)
                        case["keyboard_screenshot"]=shot
                        page.keyboard.press("Escape")
                        assert match(state(page),initial),"Escape no restore"
                        case["escape_reset"]=True

                        surface.focus()
                        a=state(page)
                        box=surface.bounding_box()
                        assert box and box["width"]>30 and box["height"]>30
                        x=box["x"]+box["width"]*.50
                        y=box["y"]+box["height"]*.55
                        page.mouse.move(x,y)
                        page.mouse.down()
                        page.mouse.move(x+65,y+24,steps=8)
                        page.mouse.up()
                        page.wait_for_timeout(180)
                        b=state(page)
                        assert changed(b,a,orbit_key),"Mouse orbit regression"
                        page.mouse.wheel(0,-160)
                        page.wait_for_timeout(150)
                        c=state(page)
                        assert changed(c,b,zoom_key),"Mouse wheel regression"
                        case["pointer"]={"before":a,"after_orbit":b,"after_wheel":c}
                        case["pointer_pass"]=True

                        surface.focus()
                        page.keyboard.press("Escape")
                        assert match(state(page),initial),"Escape after pointer no restore"
                        assert not case["page_errors"] and not case["external"] and not case["request_failed"]
                        case["status"]="REAL_CAMERA_KEYBOARD_AND_POINTER_PASS"
                        shot="final_"+kind+"_"+str(width)+"x"+str(height)+".png"
                        page.screenshot(path=str(OUT/shot),timeout=9000)
                        case["final_screenshot"]=shot
                    except Exception as e:
                        case["status"]="BLOCKED"
                        case["error"]=str(e)[:1600]
                        try:
                            shot="error_"+kind+"_"+str(width)+"x"+str(height)+".png"
                            page.screenshot(path=str(OUT/shot),timeout=4000)
                            case["diagnostic_screenshot"]=shot
                        except Exception:pass
                    finally:
                        report["cases"].append(case)
                        print("CAMERA_QA",kind,width,height,case["status"],case.get("error",""),flush=True)
                        ctx.close()
            browser.close()
        total=sum(c["status"]=="REAL_CAMERA_KEYBOARD_AND_POINTER_PASS" for c in report["cases"])
        report["passed"]=total
        report["gate"]="CAMERA_QA_PASS_NOT_PRODUCT_ACCEPTED" if total==9 else "BLOCKED_CAMERA_QA"
    except Exception as e:
        report["gate"]="BLOCKED_PREFLIGHT"
        report["preflight_error"]=repr(e)
    finally:
        if server:
            server.shutdown()
            server.server_close()
        (OUT/"camera_qa_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),
            encoding="utf8")
        print("CAMERA_FINAL",report["gate"],report.get("passed",0),"/9",flush=True)
    return 0 if report["gate"]=="CAMERA_QA_PASS_NOT_PRODUCT_ACCEPTED" else 1

if __name__=="__main__":
    raise SystemExit(run())
