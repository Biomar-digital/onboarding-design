import {chromium} from 'playwright-core'; import http from 'http'; import fs from 'fs'; import path from 'path';
const srv=http.createServer((q,s)=>{const f='.'+decodeURIComponent(q.url.split('?')[0]);const t={'.html':'text/html','.js':'text/javascript','.glb':'model/gltf-binary'}[path.extname(f)]||'application/octet-stream';fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);s.end();}else{s.writeHead(200,{'Content-Type':t});s.end(d);}})}).listen(8794);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage(); p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto(`http://localhost:8794/v14.html?w=160`); await p.waitForFunction('window.ready',null,{timeout:300000});
const r=await p.evaluate(()=>{ const bad=[]; for(let f=1;f<=360;f++){ const n=window.__audit(f); if(n) bad.push([f,n]); } return bad; });
console.log('frames with overlap:',r.length, JSON.stringify(r.slice(0,20)));
await b.close(); srv.close();
