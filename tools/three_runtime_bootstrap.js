/* FC02: guard actual Three.js startup; never substitute a simulated renderer. */
(() => {
  "use strict";
  const host=document.getElementById("viewport");
  const source=document.getElementById("hsThreeSource");
  const canvas=document.getElementById("gl");
  function fail(reason){
    window.__hsThreeReady=false;
    document.body.dataset.hsRuntimeFailed="true";
    const style=document.createElement("style");
    style.textContent='body[data-hs-runtime-failed] #gl,body[data-hs-runtime-failed] .hud,body[data-hs-runtime-failed] .overlay,body[data-hs-runtime-failed] .tip,body[data-hs-runtime-failed] .inspector{display:none!important}.hs-runtime-error{position:relative;z-index:100;margin:16px;padding:16px;border-radius:8px;background:#0c1828;color:#f4f7fa;border:2px solid #a5c6e6;max-width:440px;line-height:1.5}.hs-runtime-error button,.hs-runtime-error a{display:inline-block;margin:8px 8px 0 0;padding:10px;color:#f4f7fa;background:#243c56;border:1px solid #a5c6e6;border-radius:5px}';
    document.head.appendChild(style);
    for(const e of document.querySelectorAll('button,input,textarea,select')) e.disabled=true;
    const state=document.getElementById("state");if(state)state.textContent="3D UNAVAILABLE";
    const box=document.createElement("div");box.className="hs-runtime-error";
    box.setAttribute("role","alert");box.dataset.hsRuntimeError=reason;
    const title=document.createElement("strong");title.textContent="Không thể khởi tạo 3D / WebGL.";
    const detail=document.createElement("p");detail.textContent=reason==="BUNDLE_MISSING"?"Thiếu thư viện Three.js cục bộ. Kiểm tra hoặc build lại bộ runtime, sau đó tải lại.":reason==="WEBGL_UNAVAILABLE"?"WebGL không khả dụng. Kiểm tra trình duyệt hoặc GPU, sau đó tải lại.":"Runtime 3D chưa hoàn thành khởi tạo. Kiểm tra bộ build và tải lại.";
    const retry=document.createElement("button");retry.type="button";retry.textContent="Tải lại / Retry";retry.addEventListener("click",()=>location.reload());
    const back=document.createElement("a");back.href="../../index.html";back.textContent="Quay lại Local Runtime";
    box.append(title,detail,retry,back);(host||document.body).append(box);
    console.error("HS-3D startup blocked:",reason);
  }
  if(!host||!source||!canvas){fail("STARTUP_INCOMPLETE");return;}
  if(!window.THREE||typeof THREE.WebGLRenderer!=="function"){fail("BUNDLE_MISSING");return;}
  try{
    window.__hsThreeRenderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true});
  }catch(error){
    console.error("HS-3D real renderer construction failed",error);
    fail("WEBGL_UNAVAILABLE");return;
  }
  const script=document.createElement("script");script.textContent=source.textContent;
  source.after(script);
  if(window.__hsThreeReady!==true){
    if(window.__hsThreeRenderer){window.__hsThreeRenderer.dispose();delete window.__hsThreeRenderer;}
    fail("STARTUP_INCOMPLETE");
  }
})();
