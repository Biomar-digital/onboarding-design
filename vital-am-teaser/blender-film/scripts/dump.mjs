import {chromium} from 'playwright-core'; import http from 'http'; import fs from 'fs'; import path from 'path';
const [A,B,out]=[+process.argv[2],+process.argv[3],process.argv[4]];
const srv=http.createServer((q,s)=>{const f='.'+decodeURIComponent(q.url.split('?')[0]);const t={'.html':'text/html','.js':'text/javascript','.json':'application/json','.glb':'model/gltf-binary'}[path.extname(f)]||'application/octet-stream';fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);s.end();}else{s.writeHead(200,{'Content-Type':t});s.end(d);}})}).listen(8870);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage(); p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto(`http://localhost:8870/v20x.html?w=320`); await p.waitForFunction('window.ready',null,{timeout:300000});
const N=await p.evaluate(()=>window.__NOUT); console.log('frames',N);
fs.writeFileSync(out+'.names.json',JSON.stringify(await p.evaluate(()=>window.__names())));
const fd=fs.openSync(out,'w');
for(let F=A;F<=Math.min(B,N);F++){ const d=await p.evaluate(F=>window.__dumpFrame(F),F); fs.writeSync(fd,JSON.stringify(d)+'\n'); if(F%50===0) console.log('F',F); }
fs.closeSync(fd); await b.close(); srv.close();
