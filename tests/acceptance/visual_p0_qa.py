"""G0-V01 measured Chromium visual framing/label assertions; not owner visual acceptance."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, http.server, json, threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
SITE=ROOT/"runtime_dist"
OUT=ROOT/"tests"/"visual_output"
SIZES=((1440,900),(800,900),(390,844))
PTH="visual/3d_threejs_prototype/index.html"
PIN="293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(SITE),**kw)
    def log_message(self,*a):pass

def case_check(page,width,height):
    page.wait_for_function("() => !!window.__hsVisualQA && !!window.__hsCameraQA",timeout=15000)
    page.wait_for_timeout(220)
    initial=page.evaluate("() => window.__hsVisualQA.getMetrics()")
    assert initial["hardwareFullyVisible"],"Default model clipped: "+json.dumps(initial)
    assert initial["fitInfo"]["attempts"]<=25
    page.locator("#btnEngineer").click()
    page.wait_for_timeout(220)
    metrics=page.evaluate("() => window.__hsVisualQA.getMetrics()")
    assert metrics["engineering"] is True
    assert metrics["hardwareFullyVisible"],"Engineering model clipping: "+json.dumps(metrics)
    assert not metrics["labelOverlap"],"Overlapping Engineering labels"
    assert not metrics["labelsHitControls"],"Labels cover HUD or control buttons"
    assert metrics["oldSpritesVisible"]==0,"Old sprite labels still drawn over hardware"
    assert len(metrics["labels"])==(1 if width<=600 else 4)
    for item in metrics["labels"]:
        assert item["top"]>=0 and item["bottom"]<=metrics["safe"]["h"],"Offscreen label"
        assert item["left"]>=0 and item["right"]<=metrics["safe"]["w"],"Offscreen label"
        assert item["bottom"]<=metrics["box"]["top"]-1, "Label occludes 3D model"
    if width<=600:
        picker=page.locator("#hsVisualPicker")
        assert picker.is_visible()
        picker.select_option("2")
        page.wait_for_timeout(100)
        chosen=page.evaluate("() => window.__hsVisualQA.getMetrics()")
        assert chosen["labels"][0]["id"]=="C1","Mobile label picker not applied"
        assert not chosen["labelOverlap"]
        for button in page.locator(".overlay button").all():
            box=button.bounding_box()
            assert box and box["height"]>=44 and box["width"]>=44,"Mobile tap target too small"
    name="three_"+str(width)+"x"+str(height)+".png"
    page.screenshot(path=str(OUT/name),timeout=12000)
    # Restore an intentionally disturbed camera via the real Reset Camera button.
    page.locator("#gl").focus()
    page.keyboard.press("ArrowRight")
    page.keyboard.press("Equal")
    page.locator("#btnResetCam").click()
    page.wait_for_timeout(200)
    reset=page.evaluate("() => window.__hsVisualQA.getMetrics()")
    assert reset["hardwareFullyVisible"],"Reset did not restore framing: "+json.dumps(reset)
    assert not reset["labelOverlap"] and not reset["labelsHitControls"]
    return {"default":initial,"engineering":metrics,"after_reset":reset,
            "screenshot":name,"mobile_selected_label":("C1" if width<=600 else None)}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    report={"schema":"HS-G0-V01.visual-qa.v1","at":datetime.now(timezone.utc).isoformat(),
            "scope":"real Windows Chromium, actual lab projection; not owner acceptance",
            "cases":[],"gate":"BLOCKED_NOT_RUN"}
    srv=None
    try:
        digest=hashlib.sha256((ROOT/"archive"/"source_bundle"/"Hardware_Simulation_All_Prototypes_Source.zip").read_bytes()).hexdigest()
        assert digest==PIN
        assert (SITE/"vendor"/"visual-framing-labels.js").is_file()
        srv=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
        threading.Thread(target=srv.serve_forever,daemon=True).start()
        origin="http://127.0.0.1:"+str(srv.server_address[1])
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            report["browser"]=browser.version
            for width,height in SIZES:
                row={"viewport":[width,height],"status":"NOT_RUN","errors":[],"blocked_external":[],"failed_local":[]}
                context=browser.new_context(viewport={"width":width,"height":height},
                    device_scale_factor=1,service_workers="block",storage_state={"cookies":[],"origins":[]})
                page=context.new_page()
                page.on("pageerror",lambda e:row["errors"].append(str(e)))
                def route(r):
                    if r.request.url.startswith(origin+"/"):r.continue_()
                    else:row["blocked_external"].append(r.request.url);r.abort()
                context.route("**/*",route)
                page.on("requestfailed",lambda req:row["failed_local"].append(req.url) if req.url.startswith(origin+"/") else None)
                try:
                    response=page.goto(origin+"/"+PTH,wait_until="domcontentloaded",timeout=18000)
                    assert response and response.status==200
                    row.update(case_check(page,width,height))
                    assert not row["errors"] and not row["blocked_external"] and not row["failed_local"]
                    row["status"]="MEASURED_P0_PASS"
                except Exception as ex:
                    row["status"]="BLOCKED"
                    row["exception"]=str(ex)[:2500]
                    try:
                        name="blocked_"+str(width)+"x"+str(height)+".png"
                        page.screenshot(path=str(OUT/name),timeout=7000)
                        row["diagnostic_screenshot"]=name
                    except Exception as shot:row["screenshot_exception"]=str(shot)[:300]
                finally:
                    report["cases"].append(row)
                    print("VISUAL_QA",width,height,row["status"],row.get("exception",""),flush=True)
                    context.close()
            browser.close()
        report["passing"]=sum(x["status"]=="MEASURED_P0_PASS" for x in report["cases"])
        report["gate"]="MEASURED_V01_P0_PASS_NOT_OWNER_ACCEPTED" if report["passing"]==3 else "BLOCKED_P0_VISUAL_QA"
    except Exception as ex:
        report["gate"]="BLOCKED_PRECHECK"
        report["precheck_error"]=repr(ex)
    finally:
        if srv:srv.shutdown();srv.server_close()
        (OUT/"visual_qa_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
        print("VISUAL_FINAL",report["gate"],report.get("passing",0),"/3",flush=True)
    return 0 if report["gate"]=="MEASURED_V01_P0_PASS_NOT_OWNER_ACCEPTED" else 1

if __name__=="__main__":raise SystemExit(main())
