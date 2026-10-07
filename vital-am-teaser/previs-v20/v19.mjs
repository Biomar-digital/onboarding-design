import {chromium} from 'playwright-core'; import http from 'http'; import fs from 'fs'; import path from 'path';
const [A,B,Wd,dir]=[+process.argv[2],+process.argv[3],process.argv[4]||'1280',process.argv[5]||'pvframes'];
const srv=http.createServer((q,s)=>{const f='.'+decodeURIComponent(q.url.split('?')[0]);const t={'.html':'text/html','.js':'text/javascript','.json':'application/json','.glb':'model/gltf-binary'}[path.extname(f)]||'application/octet-stream';fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);s.end();}else{s.writeHead(200,{'Content-Type':t});s.end(d);}})}).listen(8818);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage(); p.on('pageerror',e=>console.log('ERR',e.message)); p.on('console',m=>{if(m.type()==='error')console.log(m.text())});
await p.goto(`http://localhost:8818/v19.html?w=${Wd}`); await p.waitForFunction('window.ready',null,{timeout:300000}); fs.mkdirSync(dir,{recursive:true});
const N=await p.evaluate(()=>window.__NOUT); console.log('frames',N); for(let f=A;f<=Math.min(B,N);f++){const d=await p.evaluate(f=>window.shotOut(f),f);fs.writeFileSync(`${dir}/p${String(f).padStart(4,'0')}.jpg`,Buffer.from(d.split(',')[1],'base64'));}
await b.close(); srv.close();
