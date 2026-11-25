"""Targeted remaining visual evidence, no global contrast certificate."""
import os, sys, json, io, math, threading, http.server, collections
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
from fc02_gap_qa import Handler,SITES,SIZES,new_page,THREE
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/"tests"/"fc02_targeted"; OUT.mkdir(parents=True,exist_ok=True)
report={"productSha":os.environ["HS_PRODUCT_SHA"],"qaSha":os.environ["GITHUB_SHA"],"cases":[],"gate":"BLOCKED","limits":["Native controls and DOM text sampled at named actual states; CSS scene physical occlusion is not automatic contrast pass","No claim of canvas/silkscreen glyph, all states, whole-product or human acceptance"]}
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
    fg=f[:3]; vals=[];glyph=[];h,w=bg.shape[:2]
    for x1,y1,x2,y2 in meta["rects"]:
        a,b,c,d=max(0,math.ceil(x1)),max(0,math.ceil(y1)),min(w,math.floor(x2)),min(h,math.floor(y2))
        if c<=a or d<=b:continue
        ar=bg[b:d,a:c].astype(float); normal=orig[b:d,a:c].astype(float)
        fl=lum(fg);bl=lum(ar);q=(np.maximum(fl,bl)+.05)/(np.minimum(fl,bl)+.05)
        vals.extend(q.ravel().tolist())
        mask=(np.abs(normal-fg).max(axis=2)<=3)&(np.abs(normal-ar).max(axis=2)>=8)
        glyph.extend(q[mask].tolist())
    return {**meta,"fullBoundsMin":min(vals) if vals else None,"glyphSampleMin":min(glyph) if glyph else None,"glyphPixels":len(glyph),"status":"BOUNDS_PASS" if vals and glyph and min(vals)>=4.5 else "UNVERIFIED_OR_BELOW"}
def v5(page,w,h):
    page.locator("#preset").click()
    before=page.evaluate("()=>({wires:wires.map(x=>[x.a.key,x.b.key]),paths:[...document.querySelectorAll('#wires path')].map(p=>p.getAttribute('d'))})")
    stage=page.locator(".stage"); board=page.locator("#bb")
    scroll=stage.evaluate("e=>({client:e.clientWidth,scroll:e.scrollWidth,role:e.getAttribute('role'),tab:e.tabIndex})")
    if w<=900:
        assert scroll["scroll"]>scroll["client"] and scroll["role"]=="region" and scroll["tab"]==0,scroll
        stage.focus();page.keyboard.press("End")
        stage.evaluate("e=>e.scrollLeft=e.scrollWidth")
        assert stage.evaluate("e=>e.scrollLeft")>0
    title=sample_text(page,page.locator(".bbtitle"),f"v5_{w}_title")
    for label in ("B","D","G"):
        row=sample_text(page,page.locator(".bb-labels span").filter(has_text=label),f"v5_{w}_row_{label}")
        report["cases"].append({"kind":"v5_row","viewport":[w,h],**row})
    stage.evaluate("e=>e.scrollLeft=0")
    for label in ("GPIO2","GND"):
        loc=page.locator('.pin[data-label="'+label+'"] .pname').first
        rec=sample_text(page,loc,f"v5_{w}_pin_{label}")
        loc.click()
        assert page.evaluate("()=>selected!==null && selected.label") == label
        page.locator("#bench").evaluate("e=>e.click()") # clear selection, never connect
        report["cases"].append({"kind":"v5_pin","viewport":[w,h],**rec})
    after=page.evaluate("()=>({wires:wires.map(x=>[x.a.key,x.b.key]),paths:[...document.querySelectorAll('#wires path')].map(p=>p.getAttribute('d'))})")
    assert before==after,(before,after)
    report["cases"].append({"kind":"v5_title_and_scroll","viewport":[w,h],"scroll":scroll,"wirePathsPreserved":True,**title})
def native_range(page,loc,key):
    loc.scroll_into_view_if_needed();loc.focus()
    # Capture native control in its real current state, with its actual geometry.
    m=loc.evaluate("""e=>{let r=e.getBoundingClientRect(),s=getComputedStyle(e);return {rect:[r.x,r.y,r.width,r.height],value:e.value,min:e.min,max:e.max,focus:e.matches(':focus-visible'),appearance:s.appearance,accent:s.accentColor}}""")
    im=image(page,key)
    x,y,w,h=m["rect"]; x,y,w,h=round(x),round(y),round(w),round(h)
    if x<0 or y<0 or x+w>im.shape[1] or y+h>im.shape[0] or h<8:return {**m,"status":"UNVERIFIED_CLIP"}
    crop=im[y:y+h,x:x+w]; cy=h//2
    # Actual center track RGB clusters, away from rounded endpoints; compare each
    # with nearby panel pixels immediately above/below the track.
    line=crop[cy,max(3,w//20):w-max(3,w//20)]
    common=collections.Counter(map(tuple,line.tolist())).most_common(4)
    panel=np.median(np.concatenate([crop[:2].reshape(-1,3),crop[-2:].reshape(-1,3)]),axis=0)
    clusters=[{"rgb":list(c),"pixels":n,"againstAdjacentPanel":ratio(c,panel)} for c,n in common if n>=max(3,w//30) and np.max(np.abs(np.array(c)-panel))>=8]
    return {**m,"panelRGB":panel.tolist(),"trackClusters":clusters,"status":"TRACK_SAMPLED_PASS" if len(clusters)>=2 and all(c["againstAdjacentPanel"]>=3 for c in clusters[:2]) else "TRACK_UNVERIFIED_OR_BELOW","thumbBoundary":"UNVERIFIED separate geometry/adjacent filled-track boundary"}
def main():
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();origin=f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True);report["browser"]=browser.version
            for w,h in SIZES:
                for j,site in enumerate(SITES):
                    ctx,page,errors,external,failed=new_page(browser,origin,w,h)
                    try:
                        page.goto(origin+"/"+site,wait_until="load")
                        if j==2:page.wait_for_function("()=>window.__hsThreeReady && renderer.info.render.calls>0")
                        if j==0:v5(page,w,h)
                        for k in range(page.locator('input[type="range"]').count()):
                            rec=native_range(page,page.locator('input[type="range"]').nth(k),f"range_{j}_{w}_{k}")
                            report["cases"].append({"kind":"native_range","site":site,"viewport":[w,h],"index":k,**rec})
                        if j==2:
                            page.evaluate("()=>scrollTo(0,0)");page.locator("#btnEngineer").click()
                            picker=page.locator("#hsVisualPicker")
                            if picker.is_visible():report["cases"].append({"kind":"select_display","viewport":[w,h],**sample_text(page,picker,f"picker_{w}")})
                        if j==3:
                            page.evaluate("()=>scrollTo(0,0)");page.locator("#top").click()
                            page.wait_for_function("()=>typeof rx==='number' && Math.abs(rx)<5")
                            for i in range(page.locator(".bbnum span").count()):
                                loc=page.locator(".bbnum span").nth(i)
                                rec=sample_text(page,loc,f"css_top_{w}_{i}")
                                report["cases"].append({"kind":"css_top_number","viewport":[w,h],**rec})
                        assert not errors and not external and not failed,(errors,external,failed)
                    except Exception as e:report["cases"].append({"kind":"exception","site":site,"viewport":[w,h],"detail":repr(e)})
                    finally:ctx.close()
            browser.close()
    finally:server.shutdown();server.server_close()
try:main()
except Exception as e:report["exception"]=repr(e)
finally:
    (OUT/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print("TARGETED",json.dumps({k:dict(collections.Counter(x.get("status","NO_STATUS") for x in report["cases"] if x["kind"]==k)) for k in sorted({x["kind"] for x in report["cases"]})}),flush=True)
# Full contrast scope still not established, no automatic acceptance.
sys.exit(1)
