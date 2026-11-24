// HS-G0-P1-001: generated visual geometry only; 1 world unit = 10 mm.
// Original procedural assets; DOIT/Wokwi outline is REFERENCE_ONLY, not certified CAD.
// All physical placements below are visual proposals; no electrical graph is changed.
const hsP1 = (() => {
  const T=THREE, unit=.1, pitch=2.54*unit;
  const mats=new Map(), geos=new Map(), dummy=new T.Object3D();
  function material(color,metalness=0,roughness=.65){
    const k=[color,metalness,roughness].join(':');
    if(!mats.has(k))mats.set(k,new T.MeshStandardMaterial({color,metalness,roughness}));
    return mats.get(k);
  }
  function geometry(key,make){if(!geos.has(key))geos.set(key,make());return geos.get(key)}
  const cube=geometry('cube',()=>new T.BoxGeometry(1,1,1));
  const cylinder=geometry('cyl',()=>new T.CylinderGeometry(1,1,1,16));
  const sphere=geometry('sphere',()=>new T.SphereGeometry(1,20,12));
  function mesh(parent,g,m,x,y,z,sx=1,sy=1,sz=1){
    const o=new T.Mesh(g,m);o.position.set(x,y,z);o.scale.set(sx,sy,sz);
    parent.add(o);return o;
  }
  function block(p,m,x,y,z,w,h,d){return mesh(p,cube,m,x,y,z,w,h,d)}
  function round(p,m,x,y,z,r,h){return mesh(p,cylinder,m,x,y,z,r,h,r)}
  function batch(parent,g,m,rows,name){
    const o=new T.InstancedMesh(g,m,rows.length);o.name=name;
    rows.forEach((v,i)=>{dummy.position.set(...v.p);dummy.scale.set(...v.s);
      dummy.rotation.set(0,0,0);dummy.updateMatrix();o.setMatrixAt(i,dummy.matrix)});
    o.instanceMatrix.needsUpdate=true;o.computeBoundingBox();o.computeBoundingSphere();parent.add(o);return o;
  }
  function rod(p,m,a,b,r=.018){
    const av=new T.Vector3(...a),bv=new T.Vector3(...b),d=bv.clone().sub(av),c=av.clone().add(bv).multiplyScalar(.5);
    const o=round(p,m,c.x,c.y,c.z,r,d.length());o.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),d.normalize());return o;
  }
  function printPlane(parent,w,d,y,draw,width,height){
    const c=document.createElement('canvas');c.width=width;c.height=height;
    draw(c.getContext('2d'),width,height);
    const texture=new T.CanvasTexture(c);texture.colorSpace=T.SRGBColorSpace;
    const o=new T.Mesh(new T.PlaneGeometry(w,d),new T.MeshBasicMaterial({map:texture,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-1}));
    o.rotation.x=-Math.PI/2;o.position.y=y;parent.add(o);return o;
  }
  const metal=material(0xc7cbd0,.78,.32),gold=material(0xc6a04b,.72,.36),
        black=material(0x242831,.03,.8),pcbMat=material(0x102d2b,.08,.52),
        solder=material(0x9ca5ab,.65,.38),abs=material(0xe7e8e2,0,.81),
        socketDark=material(0x252a30,.12,.72);
  const esp=new T.Group();esp.position.set(-4.7,.05,0);lab.add(esp);
  const pcb=selectable(new T.Group(),'ESP32 DevKit V1 · Reference','MCU board','GPIO2');esp.add(pcb);
  const boardBody=block(pcb,pcbMat,0,.08,0,2.82,.16,5.30);
  const left=['EN','VN','VP','D34','D35','D32','D33','D25','D26','D27','D14','D12','D13','GND.2','VIN'];
  const right=['D23','D22','TX0','RX0','D21','D19','D18','D5','TX2','RX2','D4','D2','D15','GND.1','3V3'];
  const pins=[];
  [left,right].forEach((names,side)=>names.forEach((id,i)=>{
    const mmX=side?26.8:1.27,mmY=5.8+i*2.54;
    pins.push({id,target:id==='D2'?'GPIO2':null,mm:[mmX,mmY],p:[(mmX-14.1)*unit,.34,(mmY-26.5)*unit],s:[.064,.34,.064]});
  }));
  const pinMesh=batch(pcb,cube,gold,pins,'30-pin header');
  pinMesh.userData.instanceIds=pins.map(p=>p.id);
  batch(pcb,cube,black,pins.map(p=>({p:[p.p[0],.22,p.p[2]],s:[.21,.12,.21]})),'header insulators');
  batch(pcb,cube,solder,pins.map(p=>({p:[p.p[0],.166,p.p[2]],s:[.23,.012,.23]})),'solder pads');
  // Illustrative module envelope, not a claim of the exact clone's WROOM revision.
  const moduleBody=block(pcb,material(0x24382e),0,.215,-1.10,1.80,.11,2.55);
  block(pcb,metal,0,.325,-.77,1.68,.21,1.83);
  block(pcb,black,0,.28,-2.02,1.77,.045,.55);
  const traces=[];for(let i=0;i<6;i++){traces.push({p:[-.60+i*.23,.31,-2.02],s:[.09,.015,.42]});if(i<5)traces.push({p:[-.485+i*.23,.31,-2.02+(i%2?.18:-.18)],s:[.23,.015,.055]})}
  batch(pcb,cube,gold,traces,'illustrative antenna traces');
  block(pcb,black,0,.22,.53,.68,.12,.68);
  const chipPins=[];for(let j=0;j<8;j++)for(const side of [-1,1]){chipPins.push({p:[side*.38,.177,.25+j*.08],s:[.15,.025,.045]},{p:[-.28+j*.08,.177,.53+side*.38],s:[.045,.025,.15]})}
  batch(pcb,cube,solder,chipPins,'SMD chip leads');
  const smd=[];for(let i=0;i<18;i++)smd.push({p:[(i%2?-.78:.78),.205,-.55+Math.floor(i/2)*.25],s:[.12,.075,.18]});
  batch(pcb,cube,material(0x9c8563),smd,'passive SMD bodies');
  // USB shell with a dark mouth and inner tongue at the lower PCB edge.
  block(pcb,metal,0,.30,2.35,.84,.28,.62);
  block(pcb,black,0,.30,2.664,.65,.17,.015);
  block(pcb,material(0x303742),0,.28,2.674,.48,.045,.012);
  for(const x of [-.78,.78]){block(pcb,metal,x,.23,1.93,.42,.12,.40);round(pcb,black,x,.315,1.93,.12,.07)}
  printPlane(pcb,2.82,5.3,.172,(ctx,w,h)=>{
    ctx.clearRect(0,0,w,h);ctx.fillStyle='#e1e6dc';ctx.font='bold 39px sans-serif';ctx.textAlign='center';ctx.fillText('ESP32 DEVKIT V1',w/2,h*.63);
    ctx.font='29px sans-serif';ctx.fillText('EN          BOOT',w/2,h*.82);ctx.fillText('REF • 30 PIN',w/2,h*.89);
    ctx.font='bold 29px monospace';ctx.textBaseline='middle';
    pins.forEach(p=>{ctx.textAlign=p.mm[0]<10?'left':'right';ctx.fillText(p.id.replace('GND.','GND'),p.mm[0]<10?w*.102:w*.898,p.mm[1]/53*h)});
  },768,1440);
  const espLedMat=new T.MeshStandardMaterial({color:0x1750ac,emissive:0x347cff,emissiveIntensity:.15});
  block(pcb,espLedMat,.48,.245,.33,.13,.09,.10);
  const bb=new T.Group();bb.position.set(1.05,-.02,.05);lab.add(bb);
  const base=selectable(new T.Group(),'BB400 · 400 sockets','Breadboard reference','OUT');bb.add(base);
  const bbBody=block(base,abs,0,.12,0,8.40,.24,4.76);
  const sockets=[];
  function socket(id,x,z,group){sockets.push({id,group,p:[x,.303,z],s:[.145,.016,.145]})}
  const rows='ABCDEFGHIJ';
  for(let r=0;r<10;r++)for(let c=0;c<30;c++){
    const z=(r<5?-1:1)*(.36+(r<5?4-r:r-5)*pitch);
    socket(rows[r]+(c+1),(c-14.5)*pitch,z,'terminal');
  }
  for(let rail=0;rail<4;rail++)for(let c=0;c<25;c++){
    const z=[-2.065,-1.811,1.811,2.065][rail];
    socket('RAIL'+(rail+1)+'-'+(c+1),(c-12)*pitch,z,'rail'+(rail+1));
  }
  // Actual square apertures in one extruded ABS deck. Recess bottoms below top
  // are one instanced mesh with stable instance IDs and pickable positions.
  const deck=new T.Shape();deck.moveTo(-4.2,-2.38);deck.lineTo(4.2,-2.38);deck.lineTo(4.2,2.38);deck.lineTo(-4.2,2.38);deck.closePath();
  sockets.forEach(s=>{
    const x=s.p[0],z=-s.p[2],r=.079,p=new T.Path();
    p.moveTo(x-r,z-r);p.lineTo(x-r,z+r);p.lineTo(x+r,z+r);p.lineTo(x+r,z-r);p.closePath();deck.holes.push(p);
  });
  const deckMesh=new T.Mesh(new T.ExtrudeGeometry(deck,{depth:.064,bevelEnabled:false,curveSegments:1,steps:1}),abs);
  deckMesh.rotation.x=-Math.PI/2;deckMesh.position.y=.24;base.add(deckMesh);
  const socketMesh=batch(base,cube,socketDark,sockets.map(s=>({p:[s.p[0],.243,s.p[2]],s:s.s})),'400 socket recess floors');
  socketMesh.userData.instanceIds=sockets.map(s=>s.id);
  block(base,material(0x9c9e99),0,.306,0,7.70,.012,.28);
  for(const [z,col] of [[-2.27,0xc84747],[-1.60,0x386db3],[1.60,0xc84747],[2.27,0x386db3]])block(base,material(col),0,.308,z,7.1,.009,.028);
  printPlane(base,8.4,4.76,.312,(ctx,w,h)=>{
    ctx.clearRect(0,0,w,h);ctx.fillStyle='#4a5054';ctx.font='bold 22px monospace';ctx.textAlign='center';ctx.textBaseline='middle';
    for(let c=0;c<30;c++){const x=((c-14.5)*pitch/8.4+.5)*w;ctx.fillText(String(c+1),x,h*.166);ctx.fillText(String(c+1),x,h*.834)}
    for(let r=0;r<10;r++){const z=(r<5?-1:1)*(.36+(r<5?4-r:r-5)*pitch);const y=(z/4.76+.5)*h;ctx.fillText(rows[r],w*.028,y);ctx.fillText(rows[r],w*.972,y)}
    ctx.fillText('BB400',w*.50,h*.5);
  },1536,870);
  const socketById=new Map(sockets.map(s=>[s.id,s]));
  const hole=id=>{const p=socketById.get(id).p;return [p[0],p[1],p[2]]};
  const contacts=[];
  function localEnd(component,id){const p=hole(id);contacts.push({component,id,status:'UNVERIFIED_CONTACT'});return p}
  const res=selectable(new T.Group(),'R1 · 220 Ω','Resistor','OUT');bb.add(res);
  const ra=localEnd('R1','E12'),rb=localEnd('R1','E15'),rx=(ra[0]+rb[0])/2;
  res.position.set(rx,.51,ra[2]);
  const body=round(res,material(0xd8bb86),0,0,0,.115,.58);body.rotation.z=Math.PI/2;
  for(const [x,col] of [[-.20,0xbb2529],[-.10,0xbb2529],[.02,0x75431e],[.20,0xcba74b]]){const b=round(res,material(col,.08,.55),x,0,0,.119,.045);b.rotation.z=Math.PI/2}
  for(const p of [ra,rb]){const x=p[0]-rx;rod(res,metal,[Math.sign(x)*.29,0,0],[x,0,0]);rod(res,metal,[x,0,0],[x,p[1]-.51,0])}
  const cap=selectable(new T.Group(),'C1 · 100 µF','Capacitor (illustrative body)','OUT');bb.add(cap);
  const ca=localEnd('C1','F19'),cb=localEnd('C1','F20'),cx=(ca[0]+cb[0])/2;cap.position.set(cx,.44,ca[2]);
  round(cap,material(0x214b80),0,.40,0,.25,.80);round(cap,metal,0,.815,0,.235,.035);
  // Type/polarity unverified: do not assert a particular polarized connection.
  for(const p of [ca,cb])rod(cap,metal,[p[0]-cx,0,0],[p[0]-cx,p[1]-.44,0]);
  const led=selectable(new T.Group(),'LED1 · Red','LED','OUT');bb.add(led);
  const la=localEnd('LED1','F23'),lb=localEnd('LED1','F24'),lx=(la[0]+lb[0])/2;led.position.set(lx,.43,la[2]);
  const ledMat=new T.MeshStandardMaterial({color:0x9f1628,roughness:.24,metalness:0,emissive:0xff2445,emissiveIntensity:0});
  round(led,ledMat,0,.135,0,.255,.27);mesh(led,sphere,ledMat,0,.27,0,.25,.27,.25);round(led,ledMat,0,.02,0,.275,.055);
  for(const p of [la,lb])rod(led,metal,[p[0]-lx,0,0],[p[0]-lx,p[1]-.43,0]);
  const ledLight=new T.PointLight(0xff334f,0,3);ledLight.position.set(0,.5,0);led.add(ledLight);
  const wires=[];
  function world(p,group){return new T.Vector3(...p).add(group.position)}
  const gpio=pins.find(p=>p.id==='D2');
  const a=world([gpio.p[0],.48,gpio.p[2]],esp),b=world(localEnd('J1','D12'),bb);
  const c=world(localEnd('J2','I24'),bb),d=world(localEnd('J2','RAIL4-22'),bb);
  function connector(p,female){
    const y=p.y+(female?.11:.13);
    block(lab,black,p.x,y,p.z,.235,.25,.235);
    if(!female)rod(lab,metal,[p.x,p.y,p.z],[p.x,y-.08,p.z],.025);
    return new T.Vector3(p.x,y+.125,p.z);
  }
  function jumper(id,from,to,female,color){
    const u=connector(from,female),v=connector(to,false),curve=new T.CatmullRomCurve3([u,u.clone().add(new T.Vector3(0,.55,0)),u.clone().lerp(v,.5).add(new T.Vector3(0,.95,0)),v.clone().add(new T.Vector3(0,.4,0)),v]);
    const w=new T.Mesh(new T.TubeGeometry(curve,32,.045,6,false),material(color,.03,.58));
    w.userData.curve=curve;w.userData.visualId=id;lab.add(w);wires.push(w);
  }
  jumper('J1',a,b,true,0x367cce);jumper('J2',c,d,false,0x30343c);
  // Avoid expensive transmission buffer / per-socket draw calls / dynamic shadows.
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));
  renderer.shadowMap.enabled=false; // explicit low-cost lighting policy; no shadow quality claim
  const mmMatrix=new T.Matrix4(),pos=new T.Vector3();
  function entries(mesh,source){
    return source.map((s,i)=>{mesh.getMatrixAt(i,mmMatrix);pos.setFromMatrixPosition(mmMatrix);
      return {id:s.id,group:s.group||null,target:s.target||null,center:pos.toArray()}});
  }
  Object.defineProperty(window,'__hsP1QA',{value:Object.freeze({
    geometry(){return {reference:'DOIT_30_PIN_REFERENCE_ONLY',mmPerWorldUnit:10,
      boardSize:[boardBody.scale.x*10,boardBody.scale.z*10],
      moduleSize:[moduleBody.scale.x*10,moduleBody.scale.z*10],
      breadboardSize:[bbBody.scale.x*10,bbBody.scale.z*10],
      pins:entries(pinMesh,pins),sockets:entries(socketMesh,sockets),
      pinInstances:pinMesh.count,socketInstances:socketMesh.count,apertures:deck.holes.length,
      visualContacts:contacts.map(x=>({...x})),jumpers:wires.map(w=>({id:w.userData.visualId,from:w.userData.curve.getPoint(0).toArray(),to:w.userData.curve.getPoint(1).toArray()})),
      contactAuthority:'UNVERIFIED_CONTACT',drawPolicy:'instanced, shared geometry/material, DPR<=1.5, shadows disabled'};
    }
  }),writable:false,configurable:false});
  return {esp,pcb,espLedMat,bb,base,res,cap,led,ledMat,ledLight,wires};
})();
const {esp,pcb,espLedMat,bb,base,res,cap,led,ledMat,ledLight,wires}=hsP1;
