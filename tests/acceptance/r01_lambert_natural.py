"""Predeclared 800x900 exact revision confirmation, no runtime mutation."""
import hashlib,json,os,statistics,subprocess,platform
from pathlib import Path
from playwright.sync_api import sync_playwright
from p1_r01_inspection_qa import PAGE,PIN,SAMPLE,percentile,start_server,geometry_check
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"tests"/"r01_lambert_natural"
REFS={"baseline":"74ab9b217257ed000c33bac21fed0fca73741339","candidate":os.environ["GITHUB_SHA"]}
# Six pairs; three AB and three BA, two blocks of three.
# No retries, exclusions, post-hoc threshold selection, or diagnostic variants.
ORDERS=[("baseline","candidate"),("candidate","baseline"),("baseline","candidate"),("candidate","baseline"),("baseline","candidate"),("candidate","baseline")]
# Observation-only instrumentation: no material or transform intervention,
# no pose lock, no skipped draws, and every original renderer.render executes.
RENDER_SAMPLE="""async ()=>{
 const original=renderer.render,stamps=[],calls=[],triangles=[],poses=[];
 renderer.render=function(...args){
   const result=original.apply(this,args);
   stamps.push(performance.now());calls.push(this.info.render.calls);
   triangles.push(this.info.render.triangles);poses.push(lab.rotation.y);return result;
 };
 try{
   const observed=await (SAMPLE_HERE)();
   for(let n=0;stamps.length<34&&n<3;n++)await new Promise(requestAnimationFrame);
   if(stamps.length<34)throw Error('Insufficient actual render calls');
   const actual=stamps.slice(8,34);
   return {...observed,renderCount:stamps.length,renderIntervals:actual.slice(1).map((x,i)=>x-actual[i]),
     renderCalls:calls.slice(8,34),renderTriangles:triangles.slice(8,34),poses:poses.slice(8,34)};
 }finally{renderer.render=original}
}""".replace("SAMPLE_HERE",SAMPLE)

def measure(browser,origin,kind,index):
    ctx=browser.new_context(viewport={"width":800,"height":900},device_scale_factor=1,service_workers="block")
    page=ctx.new_page(); errors=[];external=[];failed=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.on("requestfailed",lambda req:failed.append(req.url) if req.url.startswith(origin+"/") else None)
    def route(r):
        if r.request.url.startswith(origin+"/"):r.continue_()
        else:external.append(r.request.url);r.abort()
    ctx.route("**/*",route)
    try:
        res=page.goto(origin+"/"+PAGE,wait_until="domcontentloaded",timeout=25000)
        assert res and res.status==200
        page.wait_for_function("() => !!window.__hsVisualQA && !!window.__hsCameraQA && renderer.info.render.calls>0",timeout=25000)
        page.locator("#btnEngineer").click()
        page.wait_for_function("() => window.__hsVisualQA.getMetrics().engineering")
        m=page.evaluate("() => window.__hsVisualQA.getMetrics()")
        assert m["hardwareFullyVisible"] and not m["labelOverlap"] and not m["labelsHitControls"],m
        settings=page.evaluate("""()=>{
          const textures=new Set();
          for(const part of [pcb,base])part.traverse(o=>{
            for(const m of Array.isArray(o.material)?o.material:[o.material])
              if(m?.map?.isCanvasTexture)textures.add(m.map);
          });
          return {distance:dist,anisotropy:[...textures].map(t=>t.anisotropy),viewport:[innerWidth,innerHeight]};
        }""")
        assert settings["viewport"]==[800,900] and len(settings["anisotropy"])==2
        geometry_check(page.evaluate("() => window.__hsP1QA.geometry()"))
        material=page.evaluate("""()=>{const meshes=base.children.filter(o=>o.isMesh&&o.material?.color?.getHex()===0xe7e8e2);return {count:meshes.length,types:meshes.map(o=>o.material.type),shared:meshes.length===2&&meshes[0].material===meshes[1].material}}""")
        expected="MeshLambertMaterial" if kind=="candidate" else "MeshStandardMaterial"
        assert material=={"count":2,"types":[expected,expected],"shared":True},material
        r=page.evaluate(RENDER_SAMPLE)
        assert len(r["renderIntervals"])==25 and len(set(r["poses"]))>1, "natural idle yaw/render count not observed"
        r["renderP95Ms"]=percentile(r["renderIntervals"],.95)
        assert all(n>0 for n in r["renderCalls"])
        assert len(r["intervals"])>=20 and r["calls"]>0 and r["triangles"]>0
        r["p50Ms"]=statistics.median(r["intervals"]);r["p95Ms"]=percentile(r["intervals"],.95)
        name=f"{index+1}_{kind}_800x900.png"
        page.screenshot(path=str(OUT/name),timeout=15000)
        assert not errors and not external and not failed,(errors,external,failed)
        return {"kind":kind,"pair":index+1,"sha":REFS[kind],"sample":r,"metrics":m,"settings":settings,"material":material,"screenshot":name,"errors":errors,"external":external,"failed":failed}
    finally:ctx.close()
def summarize(rows):
    b=[r["sample"] for r in rows if r["kind"]=="baseline"]
    c=[r["sample"] for r in rows if r["kind"]=="candidate"]
    assert len(b)==len(c) and len(b)>0
    bp=statistics.median(r["p95Ms"] for r in b);cp=statistics.median(r["p95Ms"] for r in c)
    budgets=all(max(r["renderCalls"])<=65 and max(r["renderTriangles"])<=18000 and r["calls"]<=65 and r["triangles"]<=18000 and r["dpr"]<=1.5 for r in c)
    br=statistics.median(r["renderP95Ms"] for r in b);cr=statistics.median(r["renderP95Ms"] for r in c)
    same=all(r["gpu"]==b[0]["gpu"] for r in b+c)
    return {"baselineP95Ms":bp,"candidateP95Ms":cp,"p95BudgetMs":bp*1.10+3,
            "baselineP50Ms":statistics.median(r["p50Ms"] for r in b),"candidateP50Ms":statistics.median(r["p50Ms"] for r in c),
            "baselineIndividualP95":[r["p95Ms"] for r in b],"candidateIndividualP95":[r["p95Ms"] for r in c],
            "candidateCalls":[r["calls"] for r in c],"candidateTriangles":[r["triangles"] for r in c],"candidateDpr":[r["dpr"] for r in c],
            "sameRenderer":same,"renderBudgetMet":budgets,"frameBudgetMet":cp<=bp*1.10+3,
            "baselineRenderP95":br,"candidateRenderP95":cr,"actualRenderBudgetMs":br*1.10+3,"actualRenderGate":cr<=br*1.10+3,
            "pass":budgets and same and cp<=bp*1.10+3 and cr<=br*1.10+3}
def main():
    OUT.mkdir(parents=True,exist_ok=True);servers=[];origins={}
    report={"schema":"hs.g0.r01.natural-lambert.v1","refs":REFS,"qaHead":os.environ.get("GITHUB_SHA"),"viewport":[800,900],"orders":ORDERS,"platform":platform.platform(),"observations":[],"originalFailedRun":45462560681,"gate":"BLOCKED"}
    try:
        for k,sha in REFS.items():
            folder=ROOT/("_natural_"+k)
            assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=folder,text=True).strip()==sha
            assert hashlib.sha256((folder/"archive/source_bundle/Hardware_Simulation_All_Prototypes_Source.zip").read_bytes()).hexdigest()==PIN
            s,origins[k]=start_server(folder/"runtime_dist");servers.append(s)
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True);report["browser"]=browser.version
            for i,order in enumerate(ORDERS):
                for k in order:
                    r=measure(browser,origins[k],k,i)
                    report["observations"].append(r)
                    print("CONF_SAMPLE",i+1,k,r["sample"]["p95Ms"],flush=True)
            browser.close()
        rows=report["observations"]
        assert len(rows)==12
        report["overall"]=summarize(rows)
        report["blocks"]=[summarize(rows[:6]),summarize(rows[6:])]
        # Conservative uncertainty control: original formula must pass in both
        # independent 3-pair blocks AND aggregate; never discard the first failure.
        report["gate"]="NATURAL_LAMBERT_800_PASS_NOT_OWNER_ACCEPTED" if report["overall"]["pass"] and all(x["pass"] for x in report["blocks"]) else "BLOCKED_PERFORMANCE"
        print("CONF_SUMMARY",json.dumps({"overall":report["overall"],"blocks":report["blocks"]}),flush=True)
    except Exception as ex:
        report["exception"]=repr(ex);print("CONF_ERROR",repr(ex),flush=True)
    finally:
        for s in servers:s.shutdown();s.server_close()
        (OUT/"confirmation.json").write_text(json.dumps(report,indent=2),encoding="utf8")
        print("CONF_FINAL",report["gate"],flush=True)
    return 0 if report["gate"]=="NATURAL_LAMBERT_800_PASS_NOT_OWNER_ACCEPTED" else 1
if __name__=="__main__":raise SystemExit(main())
