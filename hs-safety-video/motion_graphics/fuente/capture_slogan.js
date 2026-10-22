// Capture the motion graphic frame by frame with a transparent background.
// node capture.js <fps> <outdir> [onlyT]
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const path = require('path');
(async () => {
  const fps = +process.argv[2] || 24, out = process.argv[3] || 'frames', only = process.argv[4];
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.resolve(__dirname, 'slogan.html'));
  await page.evaluate(() => document.fonts.ready);
  const times = only ? only.split(',').map(Number) : [...Array(Math.round(3 * fps)).keys()].map(i => i / fps);
  for (let i = 0; i < times.length; i++) {
    await page.evaluate(t => render(t), times[i]);
    const name = only ? `t${times[i]}.png` : `f${String(i + 1).padStart(4, '0')}.png`;
    await page.screenshot({ path: path.join(out, name), omitBackground: true });
  }
  await browser.close();
  console.log('frames', times.length);
})();
