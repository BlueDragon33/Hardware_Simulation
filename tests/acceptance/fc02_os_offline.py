"""Real OS network namespace cold boot, no browser request blocking."""
import json, os, socket, subprocess, threading, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from fc02_gap_qa import Handler, SITES, SIZES, THREE
import http.server
OUT=Path(__file__).resolve().parents[2]/"tests"/"fc02_offline_os"
OUT.mkdir(parents=True,exist_ok=True)
report={"productSha":os.environ["HS_PRODUCT_SHA"],"qaSha":os.environ["GITHUB_SHA"],"cases":[],"gate":"BLOCKED"}
def main():
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=os.environ["HS_PRODUCT_DIR"],text=True).strip()==report["productSha"]
    report["netNamespace"]=os.readlink("/proc/self/ns/net")
    report["interfaces"]=socket.if_nameindex()
    assert {name for _,name in report["interfaces"]}=={"lo"}
    report["routes"]=subprocess.check_output(["ip","route","show","table","all"],text=True)
    assert not any(line.startswith("default") for line in report["routes"].splitlines())
    with socket.socket() as s:
        s.settimeout(2)
        try:s.connect(("192.0.2.1",443))
        except OSError as e:report["nonLoopbackConnect"]={"errno":e.errno,"message":str(e)}
        else:raise AssertionError("unexpected route outside namespace")
    assert report["nonLoopbackConnect"]["errno"] in (101,113)
    assert not any(os.environ.get(k) for k in ("HTTP_PROXY","HTTPS_PROXY","ALL_PROXY","http_proxy","https_proxy","all_proxy"))
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin=f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            report["browser"]=browser.version
            for w,h in SIZES:
                for site in SITES:
                    ctx=browser.new_context(viewport={"width":w,"height":h},service_workers="block")
                    page=ctx.new_page(); row={"site":site,"viewport":[w,h],"errors":[],"external":[],"failed":[]}
                    page.on("pageerror",lambda e:row["errors"].append(str(e)))
                    page.on("request",lambda req:row["external"].append(req.url) if not req.url.startswith(origin+"/") else None)
                    page.on("requestfailed",lambda req:row["failed"].append(req.url))
                    try:
                        assert page.goto(origin+"/",wait_until="load").status==200
                        page.locator('a[href="./'+site+'"]').click()
                        page.wait_for_url(origin+"/"+site)
                        page.wait_for_load_state("load")
                        if site==THREE:
                            page.wait_for_function("() => window.__hsThreeReady && !!window.__hsVisualQA && renderer.info.render.calls>0")
                            page.locator("#btnEngineer").click()
                            page.wait_for_function("() => window.__hsVisualQA.getMetrics().engineering")
                        elif site==SITES[0]:
                            page.locator("#run").focus();page.keyboard.press("Enter")
                            page.wait_for_function("() => document.querySelector('#state')?.textContent?.includes('RUNNING')")
                        elif site==SITES[1]:page.locator("#btnEngineer").click()
                        else:page.locator("#engineering").click()
                        page.screenshot(path=str(OUT/f"boot_{SITES.index(site)}_{w}.png"))
                        assert page.reload(wait_until="load").status==200
                        if site==THREE:page.wait_for_function("() => window.__hsThreeReady && !!window.__hsVisualQA && renderer.info.render.calls>0")
                        assert not row["errors"] and not row["external"] and not row["failed"],row
                        row["status"]="PASS"
                    except Exception as e:row.update(status="BLOCKED",exception=str(e))
                    finally:ctx.close();report["cases"].append(row);print("OS_OFFLINE",json.dumps(row),flush=True)
            browser.close()
    finally:server.shutdown();server.server_close()
    assert len(report["cases"])==12 and all(x["status"]=="PASS" for x in report["cases"])
    report["gate"]="OS_NAMESPACE_OFFLINE_PASS"
try:main()
except Exception as e:report["exception"]=repr(e)
finally:(OUT/"report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
sys.exit(0 if report["gate"]=="OS_NAMESPACE_OFFLINE_PASS" else 1)
