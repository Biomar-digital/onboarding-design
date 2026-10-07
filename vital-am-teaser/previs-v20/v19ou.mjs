// over/under: renders the frames whose camera is within 12 cm of the surface with the camera forced under or above water
import {chromium} from 'playwright-core'; import http from 'http'; import fs from 'fs'; import path from 'path';
const [force,dir,port]=[process.argv[2],process.argv[3],+(process.argv[4]||8805)];
const srv=http.createServer((q,s)=>{const f='.'+decodeURIComponent(q.url.split('?')[0]);const t={'.html':'text/html','.js':'text/javascript','.glb':'model/gltf-binary'}[path.extname(f)]||'application/octet-stream';fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);s.end();}else{s.writeHead(200,{'Content-Type':t});s.end(d);}})}).listen(port);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage(); p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto(`http://localhost:${port}/v19.html?w=1280&force=${force}`); await p.waitForFunction('window.ready',null,{timeout:300000}); fs.mkdirSync(dir,{recursive:true});
const list=await p.evaluate(()=>{ const out=[]; for(let F=1;F<=window.__NOUT;F++){ const f=window.__tmap(F); if(f<300) continue; const y=window.__camYat(F); if(y!==null&&Math.abs(y)<0.12) out.push([F,y]); } return out; });
fs.writeFileSync(`${dir}/map.json`,JSON.stringify(list));
for(const [F] of list){ const d=await p.evaluate(F=>window.shotOut(F),F); fs.writeFileSync(`${dir}/p${String(F).padStart(4,'0')}.jpg`,Buffer.from(d.split(',')[1],'base64')); }
await b.close(); srv.close();
