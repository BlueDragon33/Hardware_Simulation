"""Measured final composited background diagnostic; no broad contrast certification."""
import json, os, sys, threading, http.server, math, io
from pathlib import Path
from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright
from fc02_gap_qa import Handler,SITES,SIZES,THREE,new_page
OUT=Path(__file__).resolve().parents[2]/"tests"/"fc02_composite"
OUT.mkdir(parents=True,exist_ok=True)
report={"productSha":os.environ["HS_PRODUCT_SHA"],"qaSha":os.environ["GITHUB_SHA"],"rows":[],"gate":"BLOCKED","limitations":["DOM text bounds sampled conservatively, not canvas/silkscreen glyph measurements","Visible viewport and representative normal/engineering/focus/hover states only; offscreen, unsupported compositing, nontext not globally certified","Screenshots hide text fill only for background diagnostic, restore before leaving; actual scene continues rendering","Raw metric unchanged; native ranges and selects additionally classified as nontext or unresolved displayed text, not removed or passed"]}
META=r"""() => {
 const out=[];
 const rgb=s=>{let m=s.match(/^rgba?\(([^)]+)\)$/);if(!m)return null;let v=m[1].split(',').map(Number);return v.length>=3&&v.every(Number.isFinite)?[v[0],v[1],v[2],v[3]??1]:null};
 for(const e of document.querySelectorAll('body *')){
  if(e.closest('script,style,canvas,svg')||e.matches(':disabled'))continue;
  let s=getComputedStyle(e);if(s.display==='none'||s.visibility!=='visible')continue;
  let rects=[],str=[];
  for(const n of e.childNodes){if(n.nodeType!==3||!n.textContent.trim())continue;let r=document.createRange();r.selectNodeContents(n);rects.push(...r.getClientRects());str.push(n.textContent.trim());}
  if(e.matches('input:not([type=checkbox]):not([type=radio]),textarea,select')&&(e.value||e.placeholder)){
   let b=e.getBoundingClientRect(),x=parseFloat(s.paddingLeft)||2,y=parseFloat(s.paddingTop)||2;
   rects.push({left:b.left+x+2,top:b.top+y+2,right:b.right-x-2,bottom:b.bottom-y-2});str.push(e.value||e.placeholder);
  }
  rects=rects.filter(r=>r.right>0&&r.bottom>0&&r.left<innerWidth&&r.top<innerHeight&&r.right-r.left>=1&&r.bottom-r.top>=1);
  if(!rects.length)continue;
  const reason=[];let f=rgb(s.webkitTextFillColor||s.color);
  if(!f||f[3]!==1)reason.push('foreground_alpha_or_color');
  for(let n=e;n;n=n.parentElement){let st=getComputedStyle(n);if(st.opacity!=='1'||st.mixBlendMode!=='normal'||st.filter!=='none')reason.push('ancestor_effect');}
  if(s.textShadow!=='none'||s.backgroundClip==='text'||s.webkitBackgroundClip==='text')reason.push('text_effect');
  let large=parseFloat(s.fontSize)>=24||(parseFloat(s.fontSize)>=56/3&&Number(s.fontWeight)>=700);
  // Exclude visibly occluded/partly clipped ranges from certification, not from report.
  for(const r of rects){let x=(Math.max(0,r.left)+Math.min(innerWidth,r.right))/2,y=(Math.max(0,r.top)+Math.min(innerHeight,r.bottom))/2;let top=document.elementFromPoint(x,y);if(!top||!(e===top||e.contains(top)||top.contains(e)))reason.push('occlusion_or_pointer_passthrough');}
  out.push({tag:e.tagName,inputType:e instanceof HTMLInputElement?e.type:null,selectedText:e instanceof HTMLSelectElement?e.selectedOptions[0]?.textContent:null,id:e.id,classes:String(e.className).slice(0,150),text:str.join(' ').slice(0,80),fg:f,threshold:large?3:4.5,rects:rects.map(r=>[r.left,r.top,r.right,r.bottom]),reason:[...new Set(reason)]});
 }
 return out;
}"""
def lum(rgb):
    f=np.asarray(rgb,dtype=np.float64)/255
    f=np.where(f<=.04045,f/12.92,((f+.055)/1.055)**2.4)
    return f@np.array([.2126,.7152,.0722])
def measure(page,key,only=None):
    rows=page.evaluate(META)
    if only:rows=[r for r in rows if r["id"]==only]
    normal=page.screenshot(path=str(OUT/(key+"_normal.png")),timeout=20000)
    style=page.add_style_tag(content="*{-webkit-text-fill-color:transparent!important;text-shadow:none!important;caret-color:transparent!important} *::before,*::after{-webkit-text-fill-color:transparent!important;text-shadow:none!important}")
    frames=[]
    try:
        for i in range(3):
            page.wait_for_timeout(100)
            b=page.screenshot(path=str(OUT/(key+f"_bg{i}.png")),timeout=20000)
            frames.append(lum(np.array(Image.open(io.BytesIO(b)).convert("RGB"))))
    finally:style.evaluate("(e)=>e.remove()")
    for r in rows:
        worst=None;pixels=0
        if not r["reason"]:
            fg=lum(r["fg"][:3])
            for frame in frames:
                h,w=frame.shape
                for x1,y1,x2,y2 in r["rects"]:
                    x1,y1=max(0,math.ceil(x1)),max(0,math.ceil(y1))
                    x2,y2=min(w,math.floor(x2)),min(h,math.floor(y2))
                    if x2<=x1 or y2<=y1:continue
                    bg=frame[y1:y2,x1:x2];ratio=(np.maximum(fg,bg)+.05)/(np.minimum(fg,bg)+.05)
                    val=float(ratio.min());worst=val if worst is None else min(worst,val);pixels+=ratio.size
        r.update(worstSampledRatio=worst,sampledPixels=pixels,result="UNVERIFIED" if worst is None else "SAMPLED_PASS" if worst>=r["threshold"] else "SAMPLED_FAIL")
        # Preserve identical raw metric for comparison. These are not text glyphs:
        # a native range is a meaningful nontext control, and select.value can be an
        # internal key rather than rendered option text. Neither gets automatic PASS.
        r["semanticStatus"]=("NON_TEXT_UNVERIFIED" if r.get("inputType")=="range" else
            "SELECT_TEXT_UNVERIFIED" if r["tag"]=="SELECT" else r["result"])
    return rows
def main():
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start();origin=f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True);report["browser"]=browser.version
            for w,h in SIZES:
                for j,site in enumerate(SITES):
                    ctx,page,errors,external,failed=new_page(browser,origin,w,h)
                    case={"site":site,"viewport":[w,h],"states":{}}
                    try:
                        page.goto(origin+"/"+site,wait_until="load")
                        if site==THREE:page.wait_for_function("() => window.__hsThreeReady && !!window.__hsVisualQA && renderer.info.render.calls>0")
                        case["states"]["normal"]=measure(page,f"{j}_{w}_normal")
                        button="#run" if j==0 else "#engineering" if j==3 else "#btnEngineer"
                        page.locator(button).click()
                        if j==0:page.wait_for_function("() => document.querySelector('#state')?.textContent?.includes('RUNNING')")
                        if j==2:page.wait_for_function("() => window.__hsVisualQA.getMetrics().engineering")
                        case["states"]["active"]=measure(page,f"{j}_{w}_active")
                        page.locator(button).hover()
                        case["states"]["hover"]=measure(page,f"{j}_{w}_hover",button[1:])
                        page.locator(button).focus();page.keyboard.press("Tab");page.keyboard.press("Shift+Tab")
                        case["focusObserved"]=page.locator(button).evaluate("(e)=>e.matches(':focus-visible')")
                        case["states"]["focus"]=measure(page,f"{j}_{w}_focus",button[1:])
                        assert not errors and not external and not failed,(errors,external,failed)
                    except Exception as e:case["exception"]=str(e)
                    finally:
                        ctx.close();report["rows"].append(case)
                        counts={k:sum(r["result"]==k for rs in case["states"].values() for r in rs) for k in ("SAMPLED_PASS","SAMPLED_FAIL","UNVERIFIED")}
                        print("COMPOSITE",json.dumps({"site":site,"viewport":[w,h],"counts":counts,"exception":case.get("exception")}),flush=True)
            browser.close()
    finally:server.shutdown();server.server_close()
try:main()
except Exception as e:report["exception"]=repr(e)
finally:
    (OUT/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
# This is a diagnostic, not a pass: incomplete nontext/canvas/state coverage remains explicit.
sys.exit(1)
