"""Isolated material experiment on unchanged PR16/17. Not product acceptance."""
import hashlib,json,os,statistics,subprocess,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
from p1_r01_inspection_qa import PAGE,PIN,SAMPLE,percentile,start_server,geometry_check
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"tests"/"matte_raster"
REFS={"baseline":"74ab9b217257ed000c33bac21fed0fca73741339","current":"2d6349a548abf711e942bb2d2e6f2de77d6dda41"}
# Three rotated blocks, two unmodified control conditions, one isolated intervention.
ORDERS=[("baseline","current","matte"),("matte","baseline","current"),("current","matte","baseline")]
SETUP="""mode=>{
 const before=window.__hsVisualQA.getMetrics();
 const cameraState=()=>({distance:dist,world:camera.matrixWorld.toArray(),projection:camera.projectionMatrix.toArray(),target:target.toArray()});
 const beforeCamera=cameraState();
 const meshes=base.children.filter(o=>o.isMesh&&o.material?.isMeshStandardMaterial&&o.material.color.getHex()===0xe7e8e2);
 if(meshes.length!==2||meshes[0].material!==meshes[1].material)throw Error('Unexpected ABS targets');
 const old=meshes[0].material;
 const meshState=()=>meshes.map(o=>({geometry:o.geometry.uuid,world:o.matrixWorld.toArray(),position:o.position.toArray(),scale:o.scale.toArray(),rotation:o.quaternion.toArray()}));
 const beforeMeshes=meshState();
 if(mode==='matte'){
  const m=new THREE.MeshLambertMaterial({color:old.color,side:old.side,transparent:false,depthWrite:old.depthWrite,depthTest:old.depthTest});
  for(const o of meshes)o.material=m;
 }
 const after=window.__hsVisualQA.getMetrics();
 return {before,after,beforeCamera,afterCamera:cameraState(),beforeMeshes,afterMeshes:meshState(),settings:{count:meshes.length,types:meshes.map(o=>o.material.type),geometry:meshes.map(o=>o.geometry.type),color:meshes[0].material.color.getHex(),distance:dist}};
}"""
# Instrument the same real render loop for every mode; do not replace or skip any draw.
RENDER_SAMPLE="""async ()=>{
 const original=renderer.render,stamps=[],durations=[],counts=[],triangles=[];
 renderer.render=function(...args){
   const start=performance.now();
   const result=original.apply(this,args);
   const end=performance.now();
   stamps.push(end);durations.push(end-start);counts.push(this.info.render.calls);triangles.push(this.info.render.triangles);
   return result;
 };
 try{
   const observed=await (SAMPLE_HERE)();
   const actual=stamps.slice(9);
   if(stamps.length<33||actual.length<25)throw Error('Insufficient actual renderer.render calls: '+stamps.length);
   return {...observed,renderCount:stamps.length,renderIntervals:actual.slice(1).map((x,i)=>x-actual[i]),renderCpuMs:durations.slice(9),renderCalls:counts.slice(9),renderTriangles:triangles.slice(9)};
 }finally{renderer.render=original}
}""".replace("SAMPLE_HERE",SAMPLE)
def measure(browser,origin,mode,block):
    ctx=browser.new_context(viewport={"width":800,"height":900},device_scale_factor=1,service_workers="block")
    page=ctx.new_page();errors=[];external=[];failed=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.on("requestfailed",lambda r:failed.append(r.url) if r.url.startswith(origin+"/") else None)
    def route(r):
        if r.request.url.startswith(origin+"/"):r.continue_()
        else:external.append(r.request.url);r.abort()
    ctx.route("**/*",route)
    trace={"mode":mode,"block":block+1}
    try:
        trace["stage"]="navigate"
        res=page.goto(origin+"/"+PAGE,wait_until="domcontentloaded",timeout=25000)
        assert res and res.status==200
        page.wait_for_function("() => !!window.__hsVisualQA && renderer.info.render.calls>0",timeout=25000)
        page.locator("#btnEngineer").click()
        page.wait_for_function("() => window.__hsVisualQA.getMetrics().engineering")
        trace["stage"]="before_intervention"
        # One synchronous browser task: no animation callback can run between the
        # before/after snapshots. Keep exact projection equality, no epsilon.
        trace["stage"]="intervention"
        transaction=page.evaluate(SETUP,mode)
        before,after,settings=(transaction[k] for k in ("before","after","settings"))
        trace["before"]=before
        trace["settings"]=settings
        trace["cameraAndMeshInvariants"]={k:transaction[k] for k in ("beforeCamera","afterCamera","beforeMeshes","afterMeshes")}
        assert transaction["beforeCamera"]==transaction["afterCamera"], "camera mutated by material experiment"
        assert transaction["beforeMeshes"]==transaction["afterMeshes"], "geometry mutated by material experiment"
        trace["after"]=after
        trace["stage"]="projection_and_collision"
        assert before["box"]==after["box"] and after["hardwareFullyVisible"] and not after["labelsHitControls"] and not after["labelOverlap"], "atomic projection/collision assertion"
        trace["stage"]="geometry"
        geometry_check(page.evaluate("() => window.__hsP1QA.geometry()"))
        page.wait_for_timeout(500)
        trace["stage"]="render_measurement"
        sample=page.evaluate(RENDER_SAMPLE)
        trace["sample"]=sample
        trace["stage"]="render_sample_assertions"
        assert len(sample["intervals"])>=20 and len(sample["renderIntervals"])>=24, "insufficient interval samples"
        assert all(n>0 for n in sample["renderCalls"]), "render call count zero"
        sample["p95Ms"]=percentile(sample["intervals"],.95)
        sample["p50Ms"]=statistics.median(sample["intervals"])
        sample["renderP95Ms"]=percentile(sample["renderIntervals"],.95)
        sample["renderCpuP95Ms"]=percentile(sample["renderCpuMs"],.95)
        assert not errors and not external and not failed,(errors,external,failed)
        name=f"{block+1}_{mode}.png";page.screenshot(path=str(OUT/name),timeout=15000)
        return {"mode":mode,"block":block+1,"sample":sample,"settings":settings,"atomicProjectionBefore":before["box"],"cameraAndMeshInvariants":trace["cameraAndMeshInvariants"],"metrics":after,"screenshot":name,"errors":errors,"external":external,"failed":failed}
    except Exception:
        trace["traceback"]=traceback.format_exc()
        trace["errors"]=errors;trace["external"]=external;trace["failed"]=failed
        (OUT/f"blocked_{block+1}_{mode}.json").write_text(json.dumps(trace,indent=2),encoding="utf8")
        try:page.screenshot(path=str(OUT/f"blocked_{block+1}_{mode}.png"),timeout=15000)
        except Exception:pass
        raise
    finally:ctx.close()
def main():
    OUT.mkdir(parents=True,exist_ok=True);servers=[];origins={}
    report={"schema":"hs.g0.r01.matte-raster.v1","refs":REFS,"qaHead":os.environ.get("GITHUB_SHA"),"observations":[],"orders":ORDERS,"gate":"BLOCKED","scope":"diagnostic intervention only; actual render instrumentation, no product acceptance"}
    try:
        for k,sha in REFS.items():
            folder=ROOT/("_matte_"+k)
            assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=folder,text=True).strip()==sha
            assert hashlib.sha256((folder/"archive/source_bundle/Hardware_Simulation_All_Prototypes_Source.zip").read_bytes()).hexdigest()==PIN
            srv,origins[k]=start_server(folder/"runtime_dist");servers.append(srv)
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True);report["browser"]=browser.version
            for i,order in enumerate(ORDERS):
                for mode in order:
                    r=measure(browser,origins["baseline" if mode=="baseline" else "current"],mode,i)
                    report["observations"].append(r)
                    print("MATTE_SAMPLE",i+1,mode,r["sample"]["p95Ms"],r["sample"]["renderP95Ms"],r["sample"]["renderCount"],flush=True)
            browser.close()
        summary={}
        for mode in ORDERS[0]:
            rows=[r for r in report["observations"] if r["mode"]==mode]
            assert len(rows)==3
            summary[mode]={"p95":statistics.median(r["sample"]["p95Ms"] for r in rows),"actualRenderP95":statistics.median(r["sample"]["renderP95Ms"] for r in rows),"renderCpuP95":statistics.median(r["sample"]["renderCpuP95Ms"] for r in rows),"individualP95":[r["sample"]["p95Ms"] for r in rows],"actualCounts":[r["sample"]["renderCount"] for r in rows],"area":statistics.median(r["metrics"]["box"]["width"]*r["metrics"]["box"]["height"] for r in rows)}
        b,c,m=(summary[k] for k in ("baseline","current","matte"))
        assert abs(c["area"]-m["area"])<1
        rows=[r["sample"] for r in report["observations"] if r["mode"]=="matte"]
        budgets=all(max(r["renderCalls"])<=65 and max(r["renderTriangles"])<=18000 and r["dpr"]<=1.5 for r in rows)
        same=len({r["sample"]["gpu"] for r in report["observations"]})==1
        report["summary"]=summary
        report["decision"]={"sameRenderer":same,"renderBudgetMet":budgets,"originalThreshold":b["p95"]*1.1+3,"actualRenderThreshold":b["actualRenderP95"]*1.1+3,
          "benefit":m["p95"]<c["p95"] and m["actualRenderP95"]<c["actualRenderP95"],"originalGate":m["p95"]<=b["p95"]*1.1+3,"actualRenderGate":m["actualRenderP95"]<=b["actualRenderP95"]*1.1+3}
        report["gate"]="DIAGNOSTIC_COMPLETE"
        print("MATTE_SUMMARY",json.dumps({"summary":summary,"decision":report["decision"]}),flush=True)
    except Exception as e:report["error"]=repr(e);report["traceback"]=traceback.format_exc();print("MATTE_ERROR",report["traceback"],flush=True)
    finally:
        for srv in servers:srv.shutdown();srv.server_close()
        (OUT/"matte_report.json").write_text(json.dumps(report,indent=2),encoding="utf8")
        print("MATTE_FINAL",report["gate"],flush=True)
    return 0 if report["gate"]=="DIAGNOSTIC_COMPLETE" else 1
if __name__=="__main__":raise SystemExit(main())
