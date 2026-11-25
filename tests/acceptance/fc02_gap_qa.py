"""FC02 gap diagnostics: real browser, no mocked PASS; failures retained."""
import json, hashlib, os, subprocess, threading, http.server, platform, re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
DIST=ROOT/"runtime_dist"
OUT=ROOT/"tests"/"fc02_output"
OUT.mkdir(parents=True,exist_ok=True)
SITES=("prototypes/v5_mna_solver/index.html","visual/3d_offline_prototype/index.html","visual/3d_threejs_prototype/index.html","visual/visual_prototype_1/index.html")
THREE=SITES[2]
SIZES=((1440,900),(800,900),(390,844))
PIN="293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f"
REPORT={"schema":"hs.g0.fc02.gaps.v1","sha":os.environ.get("GITHUB_SHA"),"runner":platform.platform(),"offlineIsolation":"browser route allow loopback only; NOT OS network disconnect","rows":[],"gaps":[]}
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(DIST),**kw)
    def log_message(self,*a):pass

# Measure actual computed colors, conservative classification: only fully opaque
# text against a resolved solid ancestor stack; mixed media/gradient/opacity
# remain UNVERIFIED, never inferred from tokens or screenshot appearance.
CONTRAST=r"""() => {
 const rows=[];
 const rgb=s=>{let m=s.match(/^rgba?\(([^)]+)\)$/);if(!m)return null;
 const v=m[1].split(',').map(Number);return v.length>=3&&v.every(Number.isFinite)?[v[0],v[1],v[2],v[3]??1]:null};
 const lin=x=>(x/=255)<=.04045?x/12.92:((x+.055)/1.055)**2.4;
 const lum=c=>.2126*lin(c[0])+.7152*lin(c[1])+.0722*lin(c[2]);
 function resolved(el){
  let chain=[],n=el;
  while(n){let s=getComputedStyle(n),c=rgb(s.backgroundColor);
   if(s.opacity!=='1'||s.mixBlendMode!=='normal'||s.filter!=='none'||s.backdropFilter!=='none'||s.backgroundImage!=='none'||!c)return null;
   chain.push(c);if(c[3]>=1)break;n=n.parentElement;
  }
  if(!chain.length||chain.at(-1)[3]<1)return null;
  let b=chain.pop();while(chain.length){let c=chain.pop(),a=c[3];b=[0,1,2].map(i=>c[i]*a+b[i]*(1-a)).concat(1)}return b;
 }
 for(const e of document.querySelectorAll('body *')){
  if(e.closest('script,style,svg,canvas'))continue;
  const s=getComputedStyle(e),r=e.getBoundingClientRect();
  if(s.visibility!=='visible'||s.display==='none'||!r.width||!r.height||r.bottom<=0||r.right<=0||r.top>=innerHeight||r.left>=innerWidth)continue;
  if(e.matches(':disabled'))continue;
  const text=[...e.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent.trim()).filter(Boolean).join(' ')||(e.matches('input,textarea,select')?e.value||e.placeholder:'');
  if(!text)continue;
  const f=rgb(s.color),b=resolved(e),large=parseFloat(s.fontSize)>=24||(parseFloat(s.fontSize)>=56/3&&Number(s.fontWeight)>=700),min=large?3:4.5;
  let ratio=f&&f[3]===1&&b?(Math.max(lum(f),lum(b))+.05)/(Math.min(lum(f),lum(b))+.05):null;
  // Text inside viewport can be composited over dynamic canvas through siblings.
  if(e.closest('.viewport')&&getComputedStyle(e).backgroundColor!=='rgba(0, 0, 0, 0)'&&rgb(getComputedStyle(e).backgroundColor)?.[3]!==1)ratio=null;
  if(e.closest('.viewport')&&getComputedStyle(e).backgroundColor==='rgba(0, 0, 0, 0)'&&!e.closest('.hs-v01-badge,.hs-v01-picker'))ratio=null;
  rows.push({tag:e.tagName,id:e.id,classes:String(e.className).slice(0,160),text:text.slice(0,80),fg:s.color,bg:b,ratio,min,result:ratio===null?'UNVERIFIED':ratio>=min?'PASS':'FAIL'});
 }
 return rows;
}"""
PICK_TARGET=r"""() => {
 const m=pcb.getObjectByName('30-pin header'),rect=document.querySelector('#gl').getBoundingClientRect();
 camera.updateMatrixWorld();lab.updateMatrixWorld(true);
 for(const id of ['D23','D22','D19','D18','D15','EN','VIN','D34']){
  const i=m.userData.instanceIds.indexOf(id);if(i<0)continue;
  const mat=new THREE.Matrix4();m.getMatrixAt(i,mat);
  const q=m.localToWorld(new THREE.Vector3(0,.49,0).applyMatrix4(mat)).project(camera);
  const x=rect.left+(q.x+1)*rect.width/2,y=rect.top+(1-q.y)*rect.height/2;
  if(document.elementFromPoint(x,y)!==document.querySelector('#gl'))continue;
  const ray=new THREE.Raycaster();ray.setFromCamera(new THREE.Vector2(q.x,q.y),camera);
  const hit=ray.intersectObject(m,false)[0];if(hit&&m.userData.instanceIds[hit.instanceId]===id)return {id,x,y};
 }
 return null;
}"""
OBSERVE_CLICK=r"""() => {
 const gl=document.querySelector('#gl'),m=pcb.getObjectByName('30-pin header');
 gl.addEventListener('pointerdown',e=>{
  const r=gl.getBoundingClientRect(),ray=new THREE.Raycaster();
  ray.setFromCamera(new THREE.Vector2((e.clientX-r.left)/r.width*2-1,1-(e.clientY-r.top)/r.height*2),camera);
  const hit=ray.intersectObject(m,false)[0];window.__fc02ObservedPin=hit?m.userData.instanceIds[hit.instanceId]:null;
 },{capture:true,once:true});
}"""
READ_SELECTION=r"""() => {
 const obj=typeof selectedObject==='undefined'?null:selectedObject;
 const inspector=document.querySelector('.inspector,.inspect');
 return {rayPin:window.__fc02ObservedPin??null,selectedPin:obj?.userData?.pinId??inspector?.dataset.pinId??null,selectedName:obj?.name??null,selectedData:obj?.userData?Object.keys(obj.userData):[],inspector:inspector?.innerText??null};
}"""
def new_page(browser,origin,w,h,fault=None):
    ctx=browser.new_context(viewport={"width":w,"height":h},device_scale_factor=1,service_workers="block")
    page=ctx.new_page();errors=[];external=[];failed=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.on("requestfailed",lambda req:failed.append(req.url))
    def route(r):
        url=r.request.url
        if not url.startswith(origin+"/"):external.append(url);r.abort()
        elif fault=="bundle" and url.endswith("/vendor/three-runtime.iife.js"):r.abort()
        else:r.continue_()
    ctx.route("**/*",route)
    if fault=="webgl":
        # Deliberate failure injection, never used to claim normal-render success.
        page.add_init_script("""const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(k,...a){if(/^webgl/i.test(k)||k==='experimental-webgl')return null;return original.call(this,k,...a)};""")
    return ctx,page,errors,external,failed
def snap(page,name):
    page.screenshot(path=str(OUT/(name+".png")),timeout=15000)
def record(row):
    REPORT["rows"].append(row)
    print("FC02",json.dumps({k:v for k,v in row.items() if k!="contrast"},ensure_ascii=True),flush=True)
def gap(name,detail):REPORT["gaps"].append({"name":name,"detail":detail})
def boot(browser,origin,site,w,h):
    ctx,page,errors,external,failed=new_page(browser,origin,w,h)
    row={"kind":"cold_boot","site":site,"viewport":[w,h]}
    try:
        response=page.goto(origin+"/",wait_until="load",timeout=20000)
        assert response and response.status==200
        page.locator('a[href="./'+site+'"]').click()
        page.wait_for_url(origin+"/"+site)
        page.wait_for_load_state("load")
        if site==THREE:
            page.wait_for_function("() => !!window.__hsVisualQA && renderer.info.render.calls>0",timeout=20000)
            page.locator("#btnEngineer").click()
            page.wait_for_function("() => window.__hsVisualQA.getMetrics().engineering")
        elif site==SITES[0]:
            page.locator("#run").focus();page.keyboard.press("Enter")
            page.wait_for_function("() => document.querySelector('#state')?.textContent?.includes('RUNNING')")
        elif site==SITES[1]:
            page.locator("#btnEngineer").click()
        else:page.locator("#engineering").click()
        row["contrast"]=page.evaluate(CONTRAST)
        row["contrastCounts"]={k:sum(x["result"]==k for x in row["contrast"]) for k in ("PASS","FAIL","UNVERIFIED")}
        if row["contrastCounts"]["FAIL"]:gap("contrast",{"site":site,"viewport":[w,h],"counts":row["contrastCounts"]})
        if row["contrastCounts"]["UNVERIFIED"]:gap("contrast_unverified",{"site":site,"viewport":[w,h],"counts":row["contrastCounts"]})
        snap(page,"boot_"+str(SITES.index(site))+"_"+str(w))
        page.reload(wait_until="load")
        if site==THREE:page.wait_for_function("() => !!window.__hsVisualQA && renderer.info.render.calls>0")
        assert not errors and not external and not failed,(errors,external,failed)
        row["status"]="OBSERVED"
    except Exception as e:row["status"]="BLOCKED";row["exception"]=str(e);gap("cold_boot",{"site":site,"viewport":[w,h],"exception":str(e)})
    finally:row.update(errors=errors,external=external,failed=failed);record(row);ctx.close()
def picking(browser,origin,w,h):
    ctx,page,errors,external,failed=new_page(browser,origin,w,h)
    row={"kind":"pin_pick","viewport":[w,h]}
    try:
        page.goto(origin+"/"+THREE,wait_until="load")
        page.wait_for_function("() => !!window.__hsVisualQA && renderer.info.render.calls>0")
        page.locator("#btnEngineer").click()
        page.wait_for_function("() => window.__hsVisualQA.getMetrics().engineering")
        # Focus the actual board through existing control, without changing pose or renderer.
        if page.locator("#hsVisualPicker").is_visible():page.locator("#hsVisualPicker").select_option("0")
        page.locator('.hs-v01-badge[data-component-id="GPIO2"]').click()
        page.wait_for_function("() => window.__hsVisualQA.getMetrics().focusedPart==='GPIO2'")
        target=page.evaluate(PICK_TARGET);row["target"]=target
        if not target:raise RuntimeError("No unoccluded non-D2 pin target found; picking UNVERIFIED")
        page.evaluate(OBSERVE_CLICK);page.mouse.click(target["x"],target["y"])
        row["selection"]=page.evaluate(READ_SELECTION)
        snap(page,"pin_"+str(w))
        if row["selection"]["rayPin"]!=target["id"]:raise RuntimeError("Pointer did not hit expected pin at event; UNVERIFIED")
        if row["selection"]["selectedPin"]!=target["id"]:raise RuntimeError("Real pin ray hit but stable selected pin/inspector contract not observed")
        assert page.locator(".inspector").get_attribute("data-pin-id")==target["id"]
        assert target["id"] in page.locator("#inspectTitle").inner_text()
        assert page.locator("#inspectVolt").inner_text()=="UNVERIFIED"
        assert page.locator("#inspectState").inner_text()=="UNVERIFIED_CONTACT"
        assert not errors and not external and not failed
        row["status"]="PASS"
    except Exception as e:row["status"]="BLOCKED";row["exception"]=str(e);gap("pin_pick",{"viewport":[w,h],"detail":str(e)})
    finally:row.update(errors=errors,external=external,failed=failed);record(row);ctx.close()
def failure(browser,origin,fault):
    ctx,page,errors,external,failed=new_page(browser,origin,800,900,fault)
    row={"kind":"fault","fault":fault}
    try:
        page.goto(origin+"/"+THREE,wait_until="load",timeout=20000)
        # Check visible explicit recovery UI, not browser console or generic text.
        row["alerts"]=page.locator('[role="alert"],[data-hs-runtime-error]').all_inner_texts()
        row["visibleAlerts"]=page.locator('[role="alert"]:visible,[data-hs-runtime-error]:visible').all_inner_texts()
        row["renderReady"]=page.evaluate("() => !!window.__hsVisualQA")
        snap(page,"fault_"+fault)
        if row["renderReady"] or not any(re.search(r'WebGL|Three\.js|renderer|canvas|render|3D',x,re.I) and re.search(r'retry|reload|recover|khôi phục|tải lại|thử lại|quay lại',x,re.I) for x in row["visibleAlerts"]):raise RuntimeError("Explicit visible renderer failure/recovery contract not observed")
        expected="WEBGL_UNAVAILABLE" if fault=="webgl" else "BUNDLE_MISSING"
        alert=page.locator('[data-hs-runtime-error="'+expected+'"]')
        assert alert.is_visible()
        assert alert.get_by_role("button",name="Tải lại / Retry").is_enabled()
        assert not errors, errors
        assert not external
        assert (fault=="bundle" and len(failed)==1 and failed[0].endswith("/vendor/three-runtime.iife.js")) or (fault=="webgl" and not failed)
        # Remove injected fault by opening a fresh context; use actual fallback link
        # in the failed context, then verify real renderer startup separately.
        alert.get_by_role("link",name="Quay lại Local Runtime").click()
        page.wait_for_url(origin+"/index.html")
        assert page.locator("h1").is_visible()
        row["status"]="PASS"
    except Exception as e:row["status"]="BLOCKED";row["exception"]=str(e);gap("fault_"+fault,str(e))
    finally:row.update(errors=errors,external=external,failed=failed);record(row);ctx.close()
def main():
    assert hashlib.sha256((ROOT/"archive/source_bundle/Hardware_Simulation_All_Prototypes_Source.zip").read_bytes()).hexdigest()==PIN
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin=f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True);REPORT["browser"]=browser.version
            for w,h in SIZES:
                for site in SITES:boot(browser,origin,site,w,h)
                picking(browser,origin,w,h)
            for f in ("webgl","bundle"):failure(browser,origin,f)
            browser.close()
    finally:
        server.shutdown();server.server_close()
    # §11 coverage explicitly incomplete for canvas/gradient/meaningful non-text and
    # all hover/focus states; this initial diagnostic must not promote broad PASS.
    gap("contrast_scope","canvas/silkscreen, composited backgrounds, meaningful nontext and interaction states need measured coverage")
    gap("os_offline_scope","browser loopback isolation is not OS network-disconnected boot")
if __name__=="__main__":
    try:main()
    except Exception as e:gap("harness",repr(e))
    finally:
        REPORT["gate"]="BLOCKED" if REPORT["gaps"] else "SCOPED_PASS"
        (OUT/"report.json").write_text(json.dumps(REPORT,indent=2,ensure_ascii=False),encoding="utf-8")
    raise SystemExit(1 if REPORT["gaps"] else 0)
