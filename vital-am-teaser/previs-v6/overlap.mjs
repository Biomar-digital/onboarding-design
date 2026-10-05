import {chromium} from 'playwright-core'; import http from 'http'; import fs from 'fs'; import path from 'path';
const srv=http.createServer((q,s)=>{const f='.'+decodeURIComponent(q.url.split('?')[0]);const t={'.html':'text/html','.js':'text/javascript','.glb':'model/gltf-binary'}[path.extname(f)]||'application/octet-stream';fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);s.end();}else{s.writeHead(200,{'Content-Type':t});s.end(d);}})}).listen(8774);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage(); p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('http://localhost:8774/v6.html?w=320'); await p.waitForFunction('window.ready',null,{timeout:180000});
const out=[]; for(let f=1;f<=360;f++){ out.push(await p.evaluate(f=>window.__overlap(f),f)); }
const bad=out.filter(o=>o.n>0); console.log(JSON.stringify({frames_with_overlap:bad.length,total_pairs:bad.reduce((a,o)=>a+o.n,0),worst:Math.min(...out.map(o=>o.worst)),sample:bad.slice(0,8)}));
await b.close(); srv.close();
