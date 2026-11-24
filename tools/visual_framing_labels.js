/* HS-G0-V01: generated Three.js view framing and label rail. Archive unchanged. */
(() => {
"use strict";
const host=document.getElementById("viewport");
if(!host||!window.THREE||!lab||!camera||!renderer)throw Error("V01: real Three.js scene missing");
const parts=[["GPIO2","ESP32 GPIO2",esp,pcb],["R1","R1 220Ω",res,res],["C1","C1 100µF",cap,cap],["OUT","NODE OUT",led,led]];
const oldSprites=labels;
const style=document.createElement("style");
style.id="hsV01CSS";
style.textContent=[
".hs-v01-layer{position:absolute;inset:0;z-index:5;pointer-events:none}.hs-v01-layer[hidden]{display:none!important}",
".hs-v01-svg{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}.hs-v01-svg line{stroke:#73cde9;stroke-width:1.3;stroke-dasharray:3 5}",
".hs-v01-badge{position:absolute;height:34px;padding:5px 7px;border:1px solid #56a8d6;border-radius:7px;background:rgba(3,15,27,.96);color:#ebf6ff;font:700 12px/20px system-ui,sans-serif;white-space:nowrap;text-align:center;overflow:hidden;text-overflow:ellipsis;pointer-events:auto;cursor:pointer}",
".hs-v01-badge:focus-visible,.hs-v01-picker:focus-visible{outline:3px solid #74e6da;outline-offset:1px}.hs-v01-picker{position:absolute;display:none;height:34px;pointer-events:auto;background:#0b2438;color:#eaf7ff;border:1px solid #56a8d6;border-radius:7px;font:600 12px system-ui,sans-serif}",
"@media(max-width:600px){.hs-v01-picker{display:block}}"
].join("\n");document.head.appendChild(style);
const layer=document.createElement("div");layer.className="hs-v01-layer";layer.id="hsVisualLabels";layer.hidden=true;
const svg=document.createElementNS("http://www.w3.org/2000/svg","svg");svg.classList.add("hs-v01-svg");svg.setAttribute("aria-hidden","true");layer.appendChild(svg);
const picker=document.createElement("select");picker.id="hsVisualPicker";picker.className="hs-v01-picker";picker.setAttribute("aria-label","Chọn linh kiện để xem nhãn Engineering");
parts.forEach((p,i)=>{const opt=document.createElement("option");opt.value=String(i);opt.textContent=p[1];picker.appendChild(opt)});layer.appendChild(picker);
const widgets=parts.map((p,i)=>{
 const btn=document.createElement("button");btn.className="hs-v01-badge";btn.type="button";btn.textContent=p[1];btn.dataset.componentId=p[0];
 btn.onclick=()=>{picker.value=String(i);selectedObject=p[3];showInspect(p[3]);updateLabels()};layer.appendChild(btn);
 const line=document.createElementNS("http://www.w3.org/2000/svg","line");line.dataset.componentId=p[0];svg.appendChild(line);return {btn,line};
});host.appendChild(layer);
picker.onchange=()=>{const o=parts[Number(picker.value)][3];selectedObject=o;showInspect(o);updateLabels()};
const bb=new THREE.Box3();
function points(){lab.updateWorldMatrix(true,true);bb.setFromObject(lab);if(bb.isEmpty())throw Error("V01: empty lab bounds");
 const p=[];for(const x of [bb.min.x,bb.max.x])for(const y of [bb.min.y,bb.max.y])for(const z of [bb.min.z,bb.max.z])p.push(new THREE.Vector3(x,y,z));return p;}
function project(pts,w,h){camera.updateMatrixWorld(true);let l=Infinity,r=-Infinity,t=Infinity,b=-Infinity;
 for(const p of pts){const q=p.clone().project(camera);if(!Number.isFinite(q.x)||!Number.isFinite(q.y)||q.z< -1||q.z>1)return {valid:false};
 const x=(q.x+1)*w/2,y=(1-q.y)*h/2;l=Math.min(l,x);r=Math.max(r,x);t=Math.min(t,y);b=Math.max(b,y)}
 return {valid:true,left:l,right:r,top:t,bottom:b,width:r-l,height:b-t,cx:(l+r)/2,cy:(t+b)/2};}
function local(el){if(!el||el.hidden||getComputedStyle(el).display==="none")return null;const a=el.getBoundingClientRect(),b=host.getBoundingClientRect();
 if(a.width<=0||a.height<=0||a.bottom<b.top||a.top>b.bottom)return null;
 return {left:a.left-b.left,right:a.right-b.left,top:a.top-b.top,bottom:a.bottom-b.top};}
const intersect=(a,b)=>a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top;
function safe(){const w=host.clientWidth,h=host.clientHeight,mobile=w<=600,controls=local(host.querySelector(".overlay")),
 focus=local(document.getElementById("hsCameraKeyboardStatus")),hud=local(host.querySelector(".hud"));
 const bandTop=Math.ceil(Math.max(74,...[controls,focus].filter(Boolean).map(x=>x.bottom))+8);
 const left=16,right=w-(w>=1000?244:16),top=bandTop+50,bottom=Math.min(h-12,hud?hud.top-14:h-14);
 if(right-left<90||bottom-top<80)throw Error("V01: insufficient visible scene area");
 return {w,h,mobile,left,right,top,bottom,bandTop};}
let fitInfo=null,visibleLabels=[];
function fit(){if(!host.clientWidth)return;const s=safe(),pts=points();
 target.copy(bb.getCenter(new THREE.Vector3()));dist=Math.max(14,Math.min(70,dist));
 let box=null,attempts=0;
 for(let i=0;i<25;i++){attempts=i+1;camera.clearViewOffset();updateCamera();const raw=project(pts,s.w,s.h);
 if(!raw.valid){dist*=1.4;continue}
 camera.setViewOffset(s.w,s.h,raw.cx-(s.left+s.right)/2,raw.cy-(s.top+s.bottom)/2,s.w,s.h);
 camera.updateProjectionMatrix();camera.updateMatrixWorld(true);box=project(pts,s.w,s.h);
 if(box.valid&&box.left>=s.left-.2&&box.right<=s.right+.2&&box.top>=s.top-.2&&box.bottom<=s.bottom+.2)break;
 dist=Math.min(110,dist*(box.valid?Math.max(box.width/(s.right-s.left),box.height/(s.bottom-s.top),1.05):1.5)*1.04);
 }
 fitInfo={attempts,dist,box,safe:s};if(window.__hsCameraQA?.syncInitial)window.__hsCameraQA.syncInitial();
 updateLabels();}
function anchor(obj,w,h){obj.updateWorldMatrix(true,false);const p=obj.getWorldPosition(new THREE.Vector3()).project(camera);return {x:(p.x+1)*w/2,y:(1-p.y)*h/2}}
function updateLabels(){if(!engineering||layer.hidden||!host.clientWidth)return;
 const s=safe(),w=s.w,h=s.h,ids=s.mobile?[Number(picker.value)]:[0,1,2,3],gap=8;
 picker.style.left="8px";picker.style.top=s.bandTop+"px";picker.style.width=Math.min(144,w-171)+"px";picker.style.display=s.mobile?"block":"none";
 svg.setAttribute("viewBox","0 0 "+w+" "+h);const bw=s.mobile?Math.min(165,w-170):Math.min(145,(s.right-s.left-3*gap)/4);
 const sorted=ids.map(i=>({i,p:anchor(parts[i][2],w,h)})).sort((a,b)=>a.p.x-b.p.x);
 const rects=[];sorted.forEach((o,j)=>{
 const x=s.mobile?Math.max(160,w-bw-8):s.left+j*(s.right-s.left-bw)/Math.max(1,sorted.length-1),y=s.bandTop,e=widgets[o.i];
 const rect={id:parts[o.i][0],left:x,right:x+bw,top:y,bottom:y+34};rects.push(rect);
 e.btn.hidden=false;e.btn.style.display="block";e.btn.style.left=x+"px";e.btn.style.top=y+"px";e.btn.style.width=bw+"px";
 e.line.style.display="block";e.line.setAttribute("x1",String(x+bw/2));e.line.setAttribute("y1",String(y+34));
 e.line.setAttribute("x2",String(Math.max(0,Math.min(w,o.p.x))));e.line.setAttribute("y2",String(Math.max(0,Math.min(h,o.p.y))));
 });widgets.forEach((e,i)=>{if(!ids.includes(i)){e.btn.hidden=true;e.btn.style.display="none";e.line.style.display="none"}});
 visibleLabels=rects;}
const original=setEngineering;
setEngineering=function(v){original(v);oldSprites.forEach(x=>x.visible=false);layer.hidden=!v;if(v)updateLabels()};
const reset=document.getElementById("btnResetCam").onclick;
document.getElementById("btnResetCam").onclick=()=>{reset();fit()};
let queued=false;window.addEventListener("resize",()=>{if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;fit()})},{passive:true});
function refresh(){if(engineering)updateLabels();requestAnimationFrame(refresh)}requestAnimationFrame(refresh);
fit();
Object.defineProperty(window,"__hsVisualQA",{configurable:false,writable:false,value:Object.freeze({
 fit,select(i){if(!Number.isInteger(i)||i<0||i>=parts.length)throw Error("V01: bad label index");picker.value=String(i);updateLabels()},
 getMetrics(){const s=safe(),box=project(points(),s.w,s.h),labels=visibleLabels.map(x=>({...x})),
 controlRects=[host.querySelector(".overlay"),document.getElementById("hsCameraKeyboardStatus"),host.querySelector(".hud")].map(local).filter(Boolean);
 return {box,safe:s,labels,labelOverlap:labels.some((x,i)=>labels.slice(i+1).some(y=>intersect(x,y))),
 labelsHitControls:labels.some(x=>controlRects.some(y=>intersect(x,y))),
 hardwareFullyVisible:box.valid&&box.left>=s.left-.5&&box.right<=s.right+.5&&box.top>=s.top-.5&&box.bottom<=s.bottom+.5,
 oldSpritesVisible:oldSprites.filter(x=>x.visible).length,engineering,fitInfo}}})});
})();