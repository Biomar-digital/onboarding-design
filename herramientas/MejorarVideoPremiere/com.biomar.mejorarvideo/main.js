// Mejorar Video (IA) - Premiere Pro panel (CEP, Node enabled).
// Takes the clip selected on the timeline, processes ONLY the trimmed part that is used (source in -> out),
// raises its resolution with Real-ESRGAN and its frame rate with RIFE (both on the GPU, Vulkan), keeps the
// aspect ratio, and lays the result on the track above the original at the same time position.
var cp = require('child_process'), fs = require('fs'), path = require('path'), os = require('os');

var BASE = path.join(process.env.LOCALAPPDATA || os.tmpdir(), 'MejorarVideo');
var TOOLS = path.join(BASE, 'tools');
var ESR = path.join(TOOLS, 'realesrgan', 'realesrgan-ncnn-vulkan.exe');
var RIFE_DIR = path.join(TOOLS, 'rife', 'rife-ncnn-vulkan-20221029-windows');
var RIFE = path.join(RIFE_DIR, 'rife-ncnn-vulkan.exe');
var FF = path.join(TOOLS, 'ffmpeg-master-latest-win64-gpl', 'bin', 'ffmpeg.exe');
var FP = path.join(TOOLS, 'ffmpeg-master-latest-win64-gpl', 'bin', 'ffprobe.exe');
var DL = [
  { exe: ESR, name: 'Real-ESRGAN (50 MB)', zip: 'esr.zip', into: path.join(TOOLS, 'realesrgan'),
    url: 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-windows.zip' },
  { exe: RIFE, name: 'RIFE (430 MB)', zip: 'rife.zip', into: path.join(TOOLS, 'rife'),
    url: 'https://github.com/nihui/rife-ncnn-vulkan/releases/download/20221029/rife-ncnn-vulkan-20221029-windows.zip' },
  { exe: FF, name: 'ffmpeg (200 MB)', zip: 'ffmpeg.zip', into: TOOLS,
    url: 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' }
];

var $ = function (id) { return document.getElementById(id); };
function log(msg, cls) {
  var d = document.createElement('div'); if (cls) d.className = cls; d.textContent = msg;
  $('log').appendChild(d); $('log').scrollTop = 1e9;
}
function status(msg, frac) { $('status').textContent = msg; if (frac !== undefined) $('bar').style.width = Math.round(frac * 100) + '%'; }

function evalHost(script) {
  return new Promise(function (res, rej) {
    window.__adobe_cep__.evalScript(script, function (r) {
      try { var o = JSON.parse(r); if (o.error) rej(new Error(o.error)); else res(o); }
      catch (e) { rej(new Error('Respuesta inesperada de Premiere: ' + r)); }
    });
  });
}

// runs a program; onTick (optional) is called every second while it runs (for progress by counting files)
function run(exe, args, onTick) {
  return new Promise(function (res, rej) {
    var p = cp.spawn(exe, args, { windowsHide: true }), err = '';
    p.stderr.on('data', function (d) { err = (err + d).slice(-2000); });
    var t = onTick ? setInterval(onTick, 1000) : null;
    p.on('error', function (e) { if (t) clearInterval(t); rej(e); });
    p.on('close', function (code) {
      if (t) clearInterval(t);
      if (code === 0) res(); else rej(new Error(path.basename(exe) + ' termino con error ' + code + '\n' + err.trim().split('\n').slice(-4).join('\n')));
    });
  });
}
function capture(exe, args) {
  return new Promise(function (res, rej) {
    cp.execFile(exe, args, { windowsHide: true }, function (e, out) { if (e) rej(e); else res(String(out)); });
  });
}
function countPng(dir) { try { return fs.readdirSync(dir).filter(function (f) { return /\.png$/i.test(f); }).length; } catch (e) { return 0; } }
function rmrf(dir) { try { fs.rmSync(dir, { recursive: true, force: true }); } catch (e) { try { cp.execSync('rd /s /q "' + dir + '"'); } catch (e2) {} } }
function mkdirp(d) { fs.mkdirSync(d, { recursive: true }); }

async function ensureTools() {
  mkdirp(TOOLS);
  for (var i = 0; i < DL.length; i++) {
    var t = DL[i];
    if (fs.existsSync(t.exe)) continue;
    status('Descargando ' + t.name + ' (una sola vez)...', 0);
    log('Descargando ' + t.name + '...');
    var zip = path.join(TOOLS, t.zip);
    await run('curl.exe', ['-L', '-s', '-o', zip, t.url]);
    mkdirp(t.into);
    await run('tar.exe', ['-xf', zip, '-C', t.into]);
    fs.unlinkSync(zip);
    if (!fs.existsSync(t.exe)) throw new Error('No se pudo instalar ' + t.name);
  }
}

function frac(s) { var p = String(s).trim().split('/'); return p.length === 2 ? parseFloat(p[0]) / parseFloat(p[1]) : parseFloat(p[0]); }
function tc(sec) { var m = Math.floor(sec / 60), s = sec - 60 * m; return m + 'm' + s.toFixed(2).replace('.', 's'); }

async function improve() {
  $('go').disabled = true; $('log').textContent = '';
  var tmp = null;
  try {
    var clip = await evalHost('mv_getSelectedClip()');
    $('clip').textContent = clip.name + '  (' + clip.in.toFixed(2) + 's -> ' + clip.out.toFixed(2) + 's de la fuente)';
    if (Math.abs(clip.speed - 1) > 0.001) log('Ojo: el clip tiene velocidad ' + Math.round(clip.speed * 100) + '%. Se procesa a 100% y se coloca al inicio del clip.', 'err');
    await ensureTools();

    var kind = $('kind').value, SHORT = parseInt($('res').value, 10), fpsSel = $('fps').value;
    var probe = (await capture(FP, ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate', '-of', 'csv=p=0', clip.path])).trim().split(',');
    var W = parseInt(probe[0], 10), H = parseInt(probe[1], 10), SFPS = frac(probe[2]);
    var OFPS = fpsSel === 'seq' ? clip.seqFps : (fpsSel === '0' ? SFPS : parseFloat(fpsSel));
    var interp = OFPS > SFPS + 0.01;
    var SC = kind === 'real' ? 4 : (SHORT === 0 ? 2 : Math.max(2, Math.min(4, Math.ceil(SHORT / Math.min(W, H)))));
    var MODEL = kind === 'real' ? 'realesrgan-x4plus' : 'realesr-animevideov3';
    var VF = SHORT === 0 ? 'scale=trunc(iw/2)*2:trunc(ih/2)*2:flags=lanczos'
                         : "scale='if(lte(iw,ih)," + SHORT + ",-2)':'if(lte(iw,ih),-2," + SHORT + ")':flags=lanczos";
    var RTAG = SHORT === 2160 ? '4K' : (SHORT === 1080 ? 'HD' : 'x2');
    var fpsTag = (Math.round(OFPS * 100) / 100).toString().replace('.', ',');
    log('Original ' + W + 'x' + H + ' a ' + (Math.round(SFPS * 100) / 100) + ' fps  ->  IA x' + SC + ', ' + RTAG + ', ' + fpsTag + ' fps');

    tmp = path.join(BASE, 'tmp', String(Date.now()));
    var dIn = path.join(tmp, 'in'), dUp = path.join(tmp, 'up'), dFps = path.join(tmp, 'fps');
    mkdirp(dIn); mkdirp(dUp);
    var dur = clip.out - clip.in;
    var expect = Math.max(1, Math.round(dur * SFPS));

    status('[1/4] Separando los cuadros del tramo usado...', 0.02);
    await run(FF, ['-v', 'error', '-ss', String(clip.in), '-i', clip.path, '-t', String(dur), '-an', '-fps_mode', 'passthrough', path.join(dIn, '%08d.png')]);
    var N = countPng(dIn);
    log(N + ' cuadros');

    status('[2/4] Subiendo resolucion con IA...', 0.05);
    await run(ESR, ['-i', dIn, '-o', dUp, '-n', MODEL, '-s', String(SC), '-m', path.join(TOOLS, 'realesrgan', 'models'), '-f', 'png'],
      function () { var k = countPng(dUp); status('[2/4] Subiendo resolucion con IA: ' + k + ' / ' + N, 0.05 + 0.6 * k / N); });

    var frames = dUp;
    if (interp) {
      var NT = Math.round(N * OFPS / SFPS);
      mkdirp(dFps);
      status('[3/4] Creando cuadros intermedios (RIFE)...', 0.65);
      var rargs = ['-i', dUp, '-o', dFps, '-n', String(NT), '-m', path.join(RIFE_DIR, 'rife-v4.6'), '-f', '%08d.png'];
      if (SHORT === 2160) rargs.push('-u');
      await run(RIFE, rargs, function () { var k = countPng(dFps); status('[3/4] Cuadros intermedios: ' + k + ' / ' + NT, 0.65 + 0.25 * k / NT); });
      frames = dFps;
    } else log('Cuadros por segundo: se dejan como el original.');

    var outDir = clip.project ? path.join(path.dirname(clip.project), 'Mejorados (IA)') : path.join(path.dirname(clip.path), 'Mejorados (IA)');
    mkdirp(outDir);
    var base = clip.name.replace(/\.[^.]+$/, '').replace(/[\\/:*?"<>|]/g, '_');
    var out = path.join(outDir, base + '_' + tc(clip.in) + '_' + RTAG + '_' + fpsTag + 'fps.mp4');
    status('[4/4] Armando el video...', 0.92);
    await run(FF, ['-v', 'error', '-y', '-framerate', String(OFPS), '-i', path.join(frames, '%08d.png'), '-vf', VF,
                   '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', out]);
    var size = (await capture(FP, ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', out])).trim();
    log('Listo: ' + size.replace(',', 'x') + ' a ' + fpsTag + ' fps', 'ok');
    log(out);

    status('Colocando en la linea de tiempo...', 0.98);
    var r = await evalHost('mv_importAndPlace(' + JSON.stringify(out) + ',' + clip.start + ',' + clip.track + ')');
    status(r.replaced ? 'Listo: reemplazado en la pista V' + r.track + '.' : 'Listo: colocado en la pista V' + r.track + ', encima del original.', 1);
  } catch (e) {
    status('Error', 0); log(e.message || String(e), 'err');
  } finally {
    if (tmp) rmrf(tmp);
    $('go').disabled = false;
  }
}
$('go').addEventListener('click', improve);
