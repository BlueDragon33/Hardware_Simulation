"""Diagnostic only: isolate screen coverage and texture filtering, not acceptance.
Exact PR16/PR17 checkouts. No runtime file changes or relaxed gates."""
import json, hashlib, os, statistics
from pathlib import Path
from playwright.sync_api import sync_playwright
from p1_r01_inspection_qa import PAGE, PIN, SAMPLE, percentile, start_server
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"tests"/"r01_diagnosis"
REFS={"baseline":"74ab9b217257ed000c33bac21fed0fca73741339","candidate":"2d6349a548abf711e942bb2d2e6f2de77d6dda41"}
CASES=("baseline","current","filter1","area_matched","both")
def run_case(browser,origin,mode,repeat,baseline_distance):
    ctx=browser.new_context(viewport={"width":800,"height":900},device_scale_factor=1,service_workers="block")
    page=ctx.new_page(); errors=[]; requests=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    def route(r):
        if r.request.url.startswith(origin+"/"):r.continue_()
        else:requests.append(r.request.url);r.abort()
    ctx.route("**/*",route)
    try:
        assert page.goto(origin+"/"+PAGE,wait_until="domcontentloaded",timeout=25000).status==200
        page.wait_for_function("() => !!window.__hsVisualQA && renderer.info.render.calls>0",timeout=25000)
        page.locator("#btnEngineer").click()
        page.wait_for_function("() => window.__hsVisualQA.getMetrics().engineering")
        before=page.evaluate("() => window.__hsVisualQA.getMetrics()")
        settings=page.evaluate("""([mode,bd])=>{
          const textures=new Set();
          for(const part of [pcb,base])part.traverse(o=>{
            for(const m of Array.isArray(o.material)?o.material:[o.material])
              if(m?.map?.isCanvasTexture)textures.add(m.map);
          });
          const original=[...textures].map(t=>t.anisotropy);
          if(mode==='filter1'||mode==='both')for(const t of textures){t.anisotropy=1;t.needsUpdate=true}
          if(mode==='area_matched'||mode==='both'){dist=bd;updateCamera()}
          return {original,actual:[...textures].map(t=>t.anisotropy),distance:dist};
        }""",[mode,baseline_distance])
        assert len(settings["actual"])==2,settings
        m=page.evaluate("() => window.__hsVisualQA.getMetrics()")
        assert m["hardwareFullyVisible"] and not m["labelsHitControls"] and not m["labelOverlap"]
        r=page.evaluate(SAMPLE)
        r["p50Ms"]=statistics.median(r["intervals"]);r["p95Ms"]=percentile(r["intervals"],.95)
        assert not errors and not requests
        if repeat==0:page.screenshot(path=str(OUT/(mode+".png")),timeout=15000)
        return {"mode":mode,"repeat":repeat,"settings":settings,"metrics":m,"before":before,"sample":r}
    finally:ctx.close()

def main():
    OUT.mkdir(parents=True,exist_ok=True);servers=[];origins={}
    report={"schema":"hs.g0.r01.raster-diagnostic.v1","refs":REFS,"diagnosticHead":os.environ.get("GITHUB_SHA"),"viewport":[800,900],"scope":"software renderer diagnostic only; not acceptance","observations":[]}
    try:
        for k in REFS:
            folder=ROOT/("_diag_"+k)
            assert hashlib.sha256((folder/"archive/source_bundle/Hardware_Simulation_All_Prototypes_Source.zip").read_bytes()).hexdigest()==PIN
            s,origins[k]=start_server(folder/"runtime_dist");servers.append(s)
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True);report["browser"]=browser.version
            # First baseline captures exact same-run distance for the controlled area conditions.
            first=run_case(browser,origins["baseline"],"baseline",0,None)
            bd=first["settings"]["distance"];report["observations"].append(first)
            # Rotated condition order; fresh contexts prevent simultaneous render loops.
            orders=[("current","filter1","area_matched","both"),("both","area_matched","filter1","current","baseline"),("filter1","baseline","current","both","area_matched")]
            for repeat,order in enumerate(orders):
                for mode in order:
                    rec=run_case(browser,origins["baseline" if mode=="baseline" else "candidate"],mode,repeat,bd)
                    report["observations"].append(rec)
                    print("DIAG_SAMPLE",mode,repeat,rec["sample"]["p95Ms"],rec["settings"],flush=True)
            browser.close()
        summary={}
        for mode in CASES:
            rows=[r for r in report["observations"] if r["mode"]==mode]
            assert len(rows)==3
            summary[mode]={"p95":statistics.median(r["sample"]["p95Ms"] for r in rows),"p50":statistics.median(r["sample"]["p50Ms"] for r in rows),"area":statistics.median(r["metrics"]["box"]["width"]*r["metrics"]["box"]["height"] for r in rows),"individualP95":[r["sample"]["p95Ms"] for r in rows],"calls":[r["sample"]["calls"] for r in rows],"triangles":[r["sample"]["triangles"] for r in rows]}
        report["summary"]=summary
        report["gate"]="DIAGNOSTIC_ONLY"
        print("DIAG_SUMMARY",json.dumps(summary),flush=True)
    except Exception as ex:
        report["gate"]="BLOCKED";report["error"]=repr(ex);print("DIAG_ERROR",repr(ex),flush=True)
    finally:
        for s in servers:s.shutdown();s.server_close()
        (OUT/"diagnostic.json").write_text(json.dumps(report,indent=2),encoding="utf8")
    return 0 if report["gate"]=="DIAGNOSTIC_ONLY" else 1
if __name__=="__main__":raise SystemExit(main())
