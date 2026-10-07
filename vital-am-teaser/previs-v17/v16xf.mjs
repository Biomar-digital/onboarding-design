// renders the surface-crossing output frames with the camera held under water (force=under) for the dissolve
import {chromium} from 'playwright-core'; import http from 'http'; import fs from 'fs'; import path from 'path';
const dir=process.argv[2]||'xf_under';
const srv=http.createServer((q,s)=>{const f='.'+decodeURIComponent(q.url.split('?')[0]);const t={'.html':'text/html','.js':'text/javascript','.glb':'model/gltf-binary'}[path.extname(f)]||'application/octet-stream';fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);s.end();}else{s.writeHead(200,{'Content-Type':t});s.end(d);}})}).listen(8803);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage(); p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto(`http://localhost:8803/v16.html?w=1280&force=under`); await p.waitForFunction('window.ready',null,{timeout:300000}); fs.mkdirSync(dir,{recursive:true});
const info=await p.evaluate(()=>{ const {XF0,XF1}=window.__xf(); const out=[]; for(let F=1;F<=window.__NOUT;F++){ const f=window.__tmap(F); if(f>=XF0&&f<=XF1) out.push([F,f]); } return {XF0,XF1,out}; });
fs.writeFileSync(`${dir}/map.json`,JSON.stringify(info));
for(const [F] of info.out){ const d=await p.evaluate(F=>window.shotOut(F),F); fs.writeFileSync(`${dir}/p${String(F).padStart(4,'0')}.jpg`,Buffer.from(d.split(',')[1],'base64')); }
await b.close(); srv.close();
