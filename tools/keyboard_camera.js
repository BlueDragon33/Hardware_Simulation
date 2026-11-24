/* G0 accessibility bridge for generated 3D runtime; no historical files touched. */
(() => {
  "use strict";
  const kind=document.currentScript?.dataset.hsCameraKind;
  if(!["three","canvas","css"].includes(kind))return;
  const host=document.querySelector(".viewport");
  const surface=kind==="css"?host:document.getElementById("gl");
  if(!host||!surface)throw Error("HS-CAMERA: missing camera surface");

  surface.tabIndex=0;
  surface.setAttribute("role","region");
  surface.setAttribute("aria-label","Bàn lab 3D. Tab chọn camera; mũi tên xoay; Shift+mũi tên di chuyển; cộng/trừ zoom; Escape đặt lại.");
  surface.setAttribute("aria-keyshortcuts","ArrowUp ArrowDown ArrowLeft ArrowRight Shift+ArrowUp Shift+ArrowDown Shift+ArrowLeft Shift+ArrowRight + - Escape");

  const css=document.createElement("style");
  css.id="hs-camera-keyboard-style";
  css.textContent=[
    ".hs-camera-keyboard-status{position:absolute;top:72px;left:14px;z-index:27;max-width:min(310px,calc(100% - 28px));border-radius:8px;background:rgba(4,12,21,.88);border:1px solid #42637a;color:#d8ecff;padding:7px 10px;font:11px/1.45 system-ui,sans-serif;pointer-events:none;overflow-wrap:anywhere}",
    "#gl:focus-visible,.viewport:focus-visible{outline:3px solid #73e6dc!important;outline-offset:-3px}",
    "@media(max-width:600px){.hs-camera-keyboard-status{top:126px;left:8px;max-width:calc(100% - 16px);padding:5px 7px}}"
  ].join("\n");
  document.head.appendChild(css);

  const info=document.createElement("div");
  info.id="hsCameraKeyboardStatus";
  info.className="hs-camera-keyboard-status";
  info.setAttribute("role","status");
  info.setAttribute("aria-live","polite");
  host.appendChild(info);

  const finite=(...n)=>n.every(Number.isFinite);
  // Top-level lexical camera values in the original CLASSIC scripts are
  // shared with this additional CLASSIC script. No eval and no fake camera.
  function state(){
    if(kind==="css"){
      if(!finite(rx,rz,scale,panX,panY))throw Error("HS-CAMERA: invalid CSS state");
      return {rx,rz,scale,panX,panY};
    }
    if(!finite(yaw,pitch,dist,target.x,target.y,target.z))throw Error("HS-CAMERA: invalid 3D state");
    return {yaw,pitch,dist,x:target.x,y:target.y,z:target.z};
  }
  let initial=Object.freeze(state());
  let moves=0;
  const clamp=(v,lo,hi)=>Math.min(hi,Math.max(lo,v));
  function setCamera(n){
    if(kind==="css"){
      rx=n.rx;rz=n.rz;scale=n.scale;panX=n.panX;panY=n.panY;applyCamera();
    }else{
      yaw=n.yaw;pitch=n.pitch;dist=n.dist;
      target.x=n.x;target.y=n.y;target.z=n.z;
      if(kind==="three")updateCamera();
    }
    const hud=document.getElementById("hudCam");
    if(hud)hud.textContent="Keyboard";
  }
  function move(key,shift){
    const n=state();
    const arrows=["ArrowLeft","ArrowRight","ArrowUp","ArrowDown"];
    if(!arrows.includes(key)&&!["=","+","-","_","Escape"].includes(key))return false;
    if(key==="Escape"){
      setCamera({...initial});
      const hud=document.getElementById("hudCam");
      if(hud)hud.textContent="Orbit";
      return true;
    }
    if(arrows.includes(key)&&shift){
      const d=kind==="css"?30:Math.max(.10,n.dist*.017);
      if(kind==="css"){
        if(key==="ArrowLeft")n.panX-=d;
        if(key==="ArrowRight")n.panX+=d;
        if(key==="ArrowUp")n.panY-=d;
        if(key==="ArrowDown")n.panY+=d;
      }else if(key==="ArrowLeft"||key==="ArrowRight"){
        const sign=key==="ArrowRight"?1:-1;
        n.x+=Math.cos(n.yaw)*d*sign;
        n.z-=Math.sin(n.yaw)*d*sign;
      }else n.y+=(key==="ArrowUp"?d:-d);
    }else if(arrows.includes(key)){
      if(kind==="css"){
        if(key==="ArrowLeft")n.rz-=4;
        if(key==="ArrowRight")n.rz+=4;
        if(key==="ArrowUp")n.rx=clamp(n.rx+3,28,76);
        if(key==="ArrowDown")n.rx=clamp(n.rx-3,28,76);
      }else{
        if(key==="ArrowLeft")n.yaw-=.095;
        if(key==="ArrowRight")n.yaw+=.095;
        if(key==="ArrowUp")n.pitch=clamp(n.pitch+.075,kind==="three"?-.15:-.08,kind==="three"?1.15:1.35);
        if(key==="ArrowDown")n.pitch=clamp(n.pitch-.075,kind==="three"?-.15:-.08,kind==="three"?1.15:1.35);
      }
    }else{
      const closer=key==="+"||key==="=";
      if(kind==="css")n.scale=clamp(n.scale*(closer?1.10:1/1.10),.65,1.45);
      else n.dist=clamp(n.dist*(closer?.90:1/.90),kind==="three"?5.5:6,24);
    }
    setCamera(n);return true;
  }
  function status(focused){
    host.dataset.hsCameraFocus=focused?"active":"inactive";
    const n=state(),zoom=kind==="css"?Math.round(n.scale*100)+"%":n.dist.toFixed(2);
    info.textContent=(focused?"Camera: đang điều khiển":"Tab: chọn camera")+
      " · ←→↑↓ xoay · Shift+mũi tên di chuyển · +/− zoom · Esc đặt lại · Zoom "+zoom;
  }
  surface.addEventListener("focus",()=>status(true));
  surface.addEventListener("blur",()=>status(false));
  surface.addEventListener("keydown",event=>{
    if(event.altKey||event.ctrlKey||event.metaKey)return;
    if(!move(event.key,event.shiftKey))return;
    event.preventDefault();event.stopPropagation();
    moves++;host.dataset.hsCameraMoves=String(moves);
    host.dataset.hsCameraLastKey=event.key;status(true);
  });
  Object.defineProperty(window,"__hsCameraQA",{
    configurable:false,enumerable:false,writable:false,
    value:Object.freeze({
      kind,getState:()=>Object.freeze(state()),initial:Object.freeze({...initial}),
      focused:()=>document.activeElement===surface,keyboardMoves:()=>moves,
      syncInitial:()=>{initial=Object.freeze(state());}
    })
  });
  status(false);
})();
