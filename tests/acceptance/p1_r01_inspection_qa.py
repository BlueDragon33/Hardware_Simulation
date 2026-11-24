"""P1 real Chromium paired baseline/candidate measurement and geometry proof.
Frame intervals are browser-observed, not GPU timer measurements or physical-device claims.
"""
from pathlib import Path
import hashlib, http.server, threading, json, statistics, os, math
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"tests"/"r01_output"
SITES={"baseline":ROOT/"_r01_baseline"/"runtime_dist","candidate":ROOT/"runtime_dist"}
PAGE="visual/3d_threejs_prototype/index.html"
PIN="293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f"
SIZES=((1440,900),(800,900),(390,844))

def start_server(directory):
    def handler(*args,**kw):
        return http.server.SimpleHTTPRequestHandler(*args,directory=str(directory),**kw)
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    return server,"http://127.0.0.1:"+str(server.server_address[1])

def percentile(v,q):
    return sorted(v)[math.ceil(len(v)*q)-1]

def geometry_check(g):
    assert g["reference"]=="DOIT_30_PIN_REFERENCE_ONLY"
    assert g["pinInstances"]==len(g["pins"])==30
    assert len({p["id"] for p in g["pins"]})==30
    assert g["socketInstances"]==len(g["sockets"])==g["apertures"]==400
    assert len({s["id"] for s in g["sockets"]})==400
    assert sum(s["group"]=="terminal" for s in g["sockets"])==300
    assert all(sum(s["group"]=="rail"+str(i) for s in g["sockets"])==25 for i in range(1,5))
    assert all(abs(a-b)<.001 for a,b in zip(g["boardSize"],[28.2,53]))
    assert all(abs(a-b)<.001 for a,b in zip(g["breadboardSize"],[84,47.6]))
    for group in (g["pins"][:15],g["pins"][15:]):
        assert all(abs((b["center"][2]-a["center"][2])*10-2.54)<.05 for a,b in zip(group,group[1:]))
    sockets={s["id"]:s for s in g["sockets"]}
    for row in "ABCDEFGHIJ":
        for col in range(1,30):
            assert abs((sockets[row+str(col+1)]["center"][0]-sockets[row+str(col)]["center"][0])*10-2.54)<.05
    gpio=next(p for p in g["pins"] if p["id"]=="D2")
    assert gpio["target"]=="GPIO2"
    assert len(g["leadChecks"])==6 and all(c["errorMm"]<.05 for c in g["leadChecks"])
    assert len(g["connectorChecks"])==4 and all(c["errorMm"]<.05 for c in g["connectorChecks"])
    assert all(p["expected"]==p["actual"] for p in g["picks"])
    assert len(g["jumpers"])==2 and g["contactAuthority"]=="UNVERIFIED_CONTACT"

SAMPLE="""async () => {
 const times=[];let previous=null;
 await new Promise(resolve=>{let n=0;function tick(now){
 if(previous!==null&&n>8)times.push(now-previous);previous=now;
 if(++n<34)requestAnimationFrame(tick);else resolve();
 }requestAnimationFrame(tick)});
 const gl=renderer.getContext(),ext=gl.getExtension('WEBGL_debug_renderer_info');
 return {intervals:times,calls:renderer.info.render.calls,triangles:renderer.info.render.triangles,
 geometries:renderer.info.memory.geometries,textures:renderer.info.memory.textures,
 dpr:renderer.getPixelRatio(),gpu:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER)};
}"""

def focus_check(page,w,h):
    """Use visible controls and independently projected pin-instance geometry."""
    results=[]
    def visible_metrics():
        return page.evaluate("() => window.__hsVisualQA.getMetrics()")
    for i,part in enumerate(("GPIO2","R1","C1","OUT")):
        if page.locator("#hsVisualPicker").is_visible():
            page.locator("#hsVisualPicker").select_option(str(i))
        badge=page.locator('.hs-v01-badge[data-component-id="'+part+'"]')
        badge.click()
        page.wait_for_function("(id) => window.__hsVisualQA.getMetrics().focusedPart===id",arg=part)
        page.wait_for_timeout(180)
        m=visible_metrics()
        b,s=m["focusBox"],m["safe"]
        assert b["valid"] and b["left"]>=s["left"]-1 and b["right"]<=s["right"]+1 and b["top"]>=s["top"]-1 and b["bottom"]<=s["bottom"]+1, (part,b,s)
        assert len(m["labels"])==1 and m["labels"][0]["id"]==part and not m["labelsHitControls"]
        assert min(b["width"],b["height"])>=20, (part,b)
        record={"part":part,"focusBox":b,"safe":s}
        if part=="GPIO2":
            anchor=page.evaluate("""() => {
              const p=pcb.getObjectByName('30-pin header'),idx=p.userData.instanceIds.indexOf('D2');
              const m=new THREE.Matrix4();p.getMatrixAt(idx,m);
              const actual=p.localToWorld(new THREE.Vector3(0,.5,0).applyMatrix4(m));
              const projected=actual.clone().project(camera);
              const v=document.querySelector('#viewport'),line=document.querySelector('.hs-v01-svg line[data-component-id="GPIO2"]');
              const x=(projected.x+1)*v.clientWidth/2,y=(1-projected.y)*v.clientHeight/2;
              return {index:idx,anchorErrorMm:d2Anchor.getWorldPosition(new THREE.Vector3()).distanceTo(actual)*10,
                leaderErrorPx:Math.hypot(x-Number(line.getAttribute('x2')),y-Number(line.getAttribute('y2'))),
                expected:[x,y],actual:[Number(line.getAttribute('x2')),Number(line.getAttribute('y2'))]};
            }""")
            assert anchor["index"]>=0 and anchor["anchorErrorMm"]<.001 and anchor["leaderErrorPx"]<=3,anchor
            record["D2"]=anchor
        name=f"focus_{part}_{w}x{h}.png"
        page.screenshot(path=str(OUT/name),timeout=15000)
        record["screenshot"]=name
        page.locator("#gl").focus()
        page.keyboard.press("Escape")
        page.wait_for_function("() => window.__hsVisualQA.getMetrics().focusedPart===null")
        assert visible_metrics()["hardwareFullyVisible"]
        record["escapeRestoredOverview"]=True
        results.append(record)
    hud=page.evaluate("""() => Array.from(document.querySelectorAll('.viewport .hud .card')).map(e=>({text:e.innerText,visible:getComputedStyle(e).display!=='none'&&e.getBoundingClientRect().height>0}))""")
    assert len(hud)==5 and all(r["visible"] for r in hud),hud
    return {"focus":results,"hud":hud}

def capture(browser,origin,kind,w,h):
    errors=[];external=[];failed=[]
    ctx=browser.new_context(viewport={"width":w,"height":h},device_scale_factor=1,service_workers="block")
    page=ctx.new_page()
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.on("requestfailed",lambda req:failed.append(req.url) if req.url.startswith(origin+"/") else None)
    def route(r):
        if r.request.url.startswith(origin+"/"):r.continue_()
        else:external.append(r.request.url);r.abort()
    ctx.route("**/*",route)
    try:
        response=page.goto(origin+"/"+PAGE,wait_until="domcontentloaded",timeout=25000)
        assert response and response.status==200
        page.wait_for_function("() => !!window.__hsVisualQA && !!window.__hsCameraQA && renderer.info.render.calls>0",timeout=25000)
        page.locator("#btnEngineer").click()
        page.wait_for_function("() => window.__hsVisualQA.getMetrics().engineering")
        metrics=page.evaluate("() => window.__hsVisualQA.getMetrics()")
        assert metrics["hardwareFullyVisible"] and not metrics["labelOverlap"] and not metrics["labelsHitControls"]
        geom=page.evaluate("() => window.__hsP1QA.geometry()")
        geometry_check(geom)
        reps=[page.evaluate(SAMPLE) for _ in range(3)]
        for r in reps:
            r["p50Ms"]=statistics.median(r["intervals"]);r["p95Ms"]=percentile(r["intervals"],.95)
            assert len(r["intervals"])>=20 and r["calls"]>0 and r["triangles"]>0
        name=f"{kind}_{w}x{h}.png"
        page.screenshot(path=str(OUT/name),timeout=15000)
        inspection=focus_check(page,w,h) if kind=="candidate" else None
        assert not errors and not external and not failed,(errors,external,failed)
        return {"status":"OBSERVED","geometry":geom,"metrics":metrics,"samples":reps,"inspection":inspection,"errors":errors,"external":external,"failed":failed,"screenshot":name}
    except Exception as e:
        page.screenshot(path=str(OUT/f"blocked_{kind}_{w}x{h}.png"),timeout=15000)
        return {"status":"BLOCKED","exception":str(e),"errors":errors,"external":external,"failed":failed}
    finally:ctx.close()

def main():
    OUT.mkdir(parents=True,exist_ok=True);servers=[];origins={}
    report={"schema":"hs.g0.p1.r01.paired-windows.v1","baselineSha":"74ab9b217257ed000c33bac21fed0fca73741339","candidateSha":os.environ.get("GITHUB_SHA"),"scope":"headless Chromium frame intervals, not GPU execution time","cases":[]}
    try:
        for kind,folder in SITES.items():
            archive=folder.parent/"archive"/"source_bundle"/"Hardware_Simulation_All_Prototypes_Source.zip"
            assert hashlib.sha256(archive.read_bytes()).hexdigest()==PIN
            s,origin=start_server(folder);servers.append(s);origins[kind]=origin
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True);report["browser"]=browser.version
            for i,(w,h) in enumerate(SIZES):
                pair={"viewport":[w,h]}
                for kind in (("baseline","candidate") if i%2==0 else ("candidate","baseline")):
                    pair[kind]=capture(browser,origins[kind],kind,w,h)
                if all(pair[k]["status"]=="OBSERVED" for k in SITES):
                    b,c=pair["baseline"]["samples"],pair["candidate"]["samples"]
                    bp=statistics.median(r["p95Ms"] for r in b);cp=statistics.median(r["p95Ms"] for r in c)
                    bc=statistics.median(r["calls"] for r in b);cc=statistics.median(r["calls"] for r in c)
                    budgets=all(r["calls"]<=65 and r["triangles"]<=18000 and r["dpr"]<=1.5 for r in c)
                    same_gpu=all(r["gpu"]==b[0]["gpu"] for r in b+c)
                    pair["comparison"]={"baselineP95Ms":bp,"candidateP95Ms":cp,"baselineDrawCalls":bc,"candidateDrawCalls":cc,
                        "baselineTriangles":statistics.median(r["triangles"] for r in b),"candidateTriangles":statistics.median(r["triangles"] for r in c),
                        "renderBudgetMet":budgets,"sameRenderer":same_gpu,
                        "baselineP50Ms":statistics.median(r["p50Ms"] for r in b),"candidateP50Ms":statistics.median(r["p50Ms"] for r in c),
                        "p95BudgetMs":bp*1.10+3,"frameBudgetMet":cp<=bp*1.10+3}
                    pair["status"]="PASS" if budgets and same_gpu and cp<=bp*1.10+3 else "BLOCKED_PERFORMANCE"
                else:pair["status"]="BLOCKED_GEOMETRY_OR_RUNTIME"
                report["cases"].append(pair)
                print("R01_PAIR",w,h,pair["status"],json.dumps(pair.get("comparison",{})),flush=True)
                for kind in SITES:
                    if pair[kind]["status"]!="OBSERVED":print("R01_ERROR",kind,pair[kind],flush=True)
            browser.close()
        report["gate"]="SCOPED_R01_QA_PASS_NOT_OWNER_ACCEPTED" if all(c["status"]=="PASS" for c in report["cases"]) and len(report["cases"])==3 else "BLOCKED"
    except Exception as e:report["gate"]="BLOCKED";report["exception"]=repr(e);print("R01_PRECHECK",repr(e),flush=True)
    finally:
        for s in servers:s.shutdown();s.server_close()
        (OUT/"p1_report.json").write_text(json.dumps(report,indent=2),encoding="utf8")
        print("R01_FINAL",report["gate"],flush=True)
    return 0 if report["gate"]=="SCOPED_R01_QA_PASS_NOT_OWNER_ACCEPTED" else 1
if __name__=="__main__":raise SystemExit(main())
