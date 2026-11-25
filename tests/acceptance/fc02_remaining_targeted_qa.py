"""Targeted remaining visual evidence, no global contrast certificate."""
import os, sys, json, io, math, threading, http.server, collections
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
from fc02_gap_qa import Handler,SITES,SIZES,new_page,THREE
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/"tests"/"fc02_remaining_targeted"; OUT.mkdir(parents=True,exist_ok=True)
report={"productSha":os.environ["HS_PRODUCT_SHA"],"qaSha":os.environ["GITHUB_SHA"],"cases":[],"gate":"BLOCKED","limits":["Exact 3139 product, missing CSS top and mobile title only; raw full bounds and solid-glyph results retained","Supplementary anti-alias ink evidence does not certify occluded or clipped glyphs; no global PASS"]}
def lum(rgb):
    a=np.asarray(rgb,dtype=float)/255.;a=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4);return a@np.array([.2126,.7152,.0722])
def ratio(a,b):
    return float((max(lum(a),lum(b))+.05)/(min(lum(a),lum(b))+.05))
def image(page,name,style=None):
    b=page.screenshot(path=str(OUT/(name+".png")),style=style,timeout=20000)
    return np.array(Image.open(io.BytesIO(b)).convert("RGB"))
def sample_text(page,loc,name):
    # All CSS/DOM and layout observed before screenshot. Raw full bounds retained;
    # observed solid glyph pixels are only a supplemental measure, not a replacement.
    loc.scroll_into_view_if_needed()
    meta=loc.evaluate("""e=>{let s=getComputedStyle(e),r=document.createRange();r.selectNodeContents(e);let rects=[...r.getClientRects()];if(e.tagName==='SELECT')rects=[e.getBoundingClientRect()];return {text:e.tagName==='SELECT'?e.selectedOptions[0]?.textContent:e.innerText,fg:s.webkitTextFillColor||s.color,bg:s.backgroundColor,rects:rects.map(b=>[b.left,b.top,b.right,b.bottom]),focus:e.matches(':focus-visible'),opacity:s.opacity,shadow:s.textShadow}}""")
    loc.evaluate("(e)=>e.setAttribute('data-fc02-target','yes')")
    try:
        orig=image(page,name+"_normal")
        bg=image(page,name+"_bg","[data-fc02-target]{-webkit-text-fill-color:transparent!important;text-shadow:none!important;caret-color:transparent!important}")
    finally:loc.evaluate("(e)=>e.removeAttribute('data-fc02-target')")
    import re
    f=[float(x) for x in re.findall(r"[\d.]+",meta["fg"])]
    if len(f) not in (3,4) or (len(f)==4 and f[3]!=1):return {**meta,"status":"UNVERIFIED_FG"}
    fg=f[:3]; vals=[];glyph=[];ink=[];h,w=bg.shape[:2]
    for x1,y1,x2,y2 in meta["rects"]:
        a,b,c,d=max(0,math.ceil(x1)),max(0,math.ceil(y1)),min(w,math.floor(x2)),min(h,math.floor(y2))
        if c<=a or d<=b:continue
        ar=bg[b:d,a:c].astype(float); normal=orig[b:d,a:c].astype(float)
        fl=lum(fg);bl=lum(ar);q=(np.maximum(fl,bl)+.05)/(np.minimum(fl,bl)+.05)
        vals.extend(q.ravel().tolist())
        mask=(np.abs(normal-fg).max(axis=2)<=3)&(np.abs(normal-ar).max(axis=2)>=8)
        glyph.extend(q[mask].tolist())
        direction=np.array(fg)-ar
        alpha=np.sum((normal-ar)*direction,axis=2)/np.maximum(1,np.sum(direction*direction,axis=2))
        residual=np.abs(normal-(ar+alpha[:,:,None]*direction)).max(axis=2)
        mask2=(alpha>=.1)&(alpha<=1.02)&(residual<=2)&(np.abs(normal-ar).max(axis=2)>=8)
        ink.extend(q[mask2].tolist())
    return {**meta,"fullBoundsMin":min(vals) if vals else None,"glyphSampleMin":min(glyph) if glyph else None,"glyphPixels":len(glyph),"antiAliasInkPixels":len(ink),"antiAliasInkRatioMin":min(ink) if ink else None,"status":"BOUNDS_PASS" if vals and glyph and min(vals)>=4.5 else "UNVERIFIED_OR_BELOW"}

def main():
    import subprocess
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()==report["productSha"]
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();origin=f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True);report["browser"]=browser.version
            for w,h in SIZES:
                ctx,page,errors,external,failed=new_page(browser,origin,w,h)
                try:
                    page.goto(origin+"/"+SITES[3],wait_until="load")
                    page.locator("#top").click()
                    # Check live camera state AND settled actual CSS matrix, not a
                    # guessed angle or arbitrary sleep. Source applyCamera uses scene.
                    page.wait_for_function("""()=>{if(rx!==70||rz!==0||scale!==.93||panX!==0||panY!==10||document.querySelector('#hudCam').textContent!=='Top')return false;const el=document.querySelector('#scene'),a=new DOMMatrix(getComputedStyle(el).transform),b=new DOMMatrix(el.style.transform);return Array.from(a.toFloat64Array()).every((v,i)=>Math.abs(v-b.toFloat64Array()[i])<.001)}""")
                    camera=page.evaluate("()=>({rx,rz,scale,panX,panY,matrix:getComputedStyle(document.querySelector('#scene')).transform})")
                    locs=page.locator(".bbnum span")
                    assert locs.count()==6
                    for i in range(6):
                        rec=sample_text(page,locs.nth(i),f"css_top_{w}_{i}")
                        report["cases"].append({"kind":"css_top_number","viewport":[w,h],"camera":camera,**rec})
                    assert not errors and not external and not failed,(errors,external,failed)
                except Exception as e:report["cases"].append({"kind":"exception","site":SITES[3],"viewport":[w,h],"detail":repr(e)})
                finally:ctx.close()
            ctx,page,errors,external,failed=new_page(browser,origin,390,844)
            try:
                page.goto(origin+"/"+SITES[0],wait_until="load")
                stage=page.locator(".stage"); title=page.locator(".bbtitle")
                stage.scroll_into_view_if_needed()
                stage.focus()
                start=stage.evaluate("e=>e.scrollLeft")
                page.keyboard.press("ArrowRight")
                page.wait_for_function("s=>document.querySelector('.stage').scrollLeft>s",arg=start)
                keyboard=stage.evaluate("e=>e.scrollLeft")
                # The prior probe scrolled to the far right, clipping the left edge
                # of title. Test the reachable center, not a redesigned board.
                geometry=page.evaluate("""()=>{const s=document.querySelector('.stage'),t=document.querySelector('.bbtitle'),r=document.createRange();r.selectNodeContents(t);const b=r.getBoundingClientRect(),c=s.getBoundingClientRect();return {textWidth:b.width,client:s.clientWidth,scrollWidth:s.scrollWidth,target:s.scrollLeft+(b.left+b.right-c.left-c.right)/2}}""")
                stage.evaluate("(e,x)=>{e.scrollLeft=x}",geometry["target"])
                page.wait_for_function("""()=>{const s=document.querySelector('.stage'),r=document.createRange();r.selectNodeContents(document.querySelector('.bbtitle'));const b=r.getBoundingClientRect(),c=s.getBoundingClientRect();return b.left>=Math.max(0,c.left)-1&&b.right<=Math.min(innerWidth,c.right)+1}""")
                rec=sample_text(page,title,"v5_390_title_center")
                rec["stageBounds"]=page.evaluate("""()=>{const s=document.querySelector('.stage'),r=document.createRange();r.selectNodeContents(document.querySelector('.bbtitle'));let a=s.getBoundingClientRect(),b=r.getBoundingClientRect();return {scroll:s.scrollLeft,stage:[a.left,a.top,a.right,a.bottom],text:[b.left,b.top,b.right,b.bottom],fullyVisible:b.left>=Math.max(0,a.left)-1&&b.right<=Math.min(innerWidth,a.right)+1&&b.top>=0&&b.bottom<=innerHeight}}""")
                report["cases"].append({"kind":"v5_mobile_title","viewport":[390,844],"keyboardScrollFrom":start,"keyboardScrollTo":keyboard,"geometry":geometry,**rec})
                assert not errors and not external and not failed,(errors,external,failed)
            except Exception as e:report["cases"].append({"kind":"exception","site":SITES[0],"viewport":[390,844],"detail":repr(e)})
            finally:ctx.close()
            browser.close()
    finally:server.shutdown();server.server_close()
try:main()
except Exception as e:report["exception"]=repr(e)
finally:
    (OUT/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    for c in report["cases"]:print("REMAINING",json.dumps(c,ensure_ascii=True),flush=True)
# Retain open gate: exact named probes are not global contrast coverage.
sys.exit(1)
