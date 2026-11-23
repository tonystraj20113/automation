import * as THREE from './three.module.js';

// The world is authored in Roblox Studio and exported as scene.js by
// src/roblox_place.py. This file only lights, frames and animates those parts.
// Pure function of t: no Date.now(), no accumulated state, no unseeded random.
const W = 1080, H = 1920;
const cv = document.getElementById('c');
const g = cv.getContext('2d');
const glCanvas = document.createElement('canvas');
glCanvas.width = W; glCanvas.height = H;

const renderer = new THREE.WebGLRenderer({
  canvas: glCanvas, antialias: true, alpha: false, preserveDrawingBuffer: true
});
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.setClearColor(0x101a33, 1);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x101a33, 24, 90);
const camera = new THREE.PerspectiveCamera(54, W / H, 0.1, 250);
scene.add(new THREE.HemisphereLight(0xe8f6ff, 0x33445e, 1.4));
const key = new THREE.DirectionalLight(0xfff2d8, 1.2);
key.position.set(8, 18, 12); scene.add(key);
const rim = new THREE.DirectionalLight(0x77c8ff, 0.7);
rim.position.set(-10, 8, -14); scene.add(rim);

const BEATS = (window.SF_TIMINGS || []).length ? window.SF_TIMINGS : [
  { t0: 0, t1: 60, caption: 'A story', title: 'STORY', move: 'push' }
];
const DUR = window.SF_DUR || BEATS[BEATS.length - 1].t1;
const PARTS = (window.SF_SCENE && window.SF_SCENE.parts) || [];
window.VH_SCENES = BEATS.map((b, i) => ({ name: `${i + 1}. ${b.title}`, t0: b.t0, t1: b.t1 }));

const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, u) => a + (b - a) * u;
const ease = x => { x = clamp(x); return x < 0.5 ? 4*x*x*x : 1 - Math.pow(-2*x + 2, 3)/2; };
const hash = n => { const v = Math.sin(n * 127.1 + 311.7) * 43758.5453; return v - Math.floor(v); };

const GEO = {
  Box: new THREE.BoxGeometry(1, 1, 1),
  Ball: new THREE.SphereGeometry(0.5, 14, 10),
  Cylinder: new THREE.CylinderGeometry(0.5, 0.5, 1, 10)
};
const matCache = new Map();
function material(hex) {
  if (!matCache.has(hex)) {
    const n = ((hex[0] << 16) | (hex[1] << 8) | hex[2]);
    matCache.set(hex, new THREE.MeshLambertMaterial({ color: n }));
  }
  return matCache.get(hex);
}

const meshes = [];
PARTS.forEach((p, i) => {
  const m = new THREE.Mesh(GEO[p.sh] || GEO.Box, material(p.c));
  m.position.set(p.p[0], p.p[1], p.p[2]);
  m.scale.set(p.s[0], p.s[1], p.s[2]);
  m.rotation.set(p.r[0], p.r[1], p.r[2], 'ZYX');
  m.userData = { part: p, baseY: p.p[1], baseZ: p.r[2], i };
  scene.add(m); meshes.push(m);
});

// ~1.15 s camera cuts. The Studio-built set changes on the story beat.
const SHOT_LEN = 1.15;
const SHOTS = [];
BEATS.forEach((b, bi) => {
  const len = Math.max(0.5, b.t1 - b.t0);
  const count = Math.max(1, Math.ceil(len / SHOT_LEN));
  for (let j = 0; j < count; j++) {
    SHOTS.push({
      a: b.t0 + len * j / count, b: b.t0 + len * (j + 1) / count,
      beat: bi, part: j, count, caption: b.caption, title: b.title,
      move: b.move || 'push', seed: bi * 97 + j
    });
  }
});
window.SF_SHOTS = SHOTS;

const CAMS = [
  { p: [10, 5.5, 15], t: [0, 2.2, 0] },
  { p: [-9, 4.4, 12], t: [0, 2.3, -4] },
  { p: [3, 9.0, 13], t: [0, 1.8, -9] },
  { p: [0, 2.7, 8], t: [0, 2.4, -8] },
  { p: [7, 3.9, 4], t: [0, 2.0, -7] },
  { p: [-4, 2.3, 6], t: [-1, 2.0, 2] },
  { p: [0, 3.2, 8], t: [0, 1.7, 0] },
  { p: [5.5, 6.5, 10], t: [0, 2.4, -3] }
];
function camFor(s) {
  const base = CAMS[s.seed % CAMS.length];
  const h1 = hash(s.seed + 1) - .5, h2 = hash(s.seed + 2) - .5, h3 = hash(s.seed + 3) - .5;
  const p0 = [base.p[0] + h1 * 2.2, base.p[1] + h2 * 1.1, base.p[2] + h3 * 1.6];
  const dir = s.move === 'pull' ? 1 : -1;
  const p1 = [p0[0] + h2 * 2.8, p0[1] + h3 * 1.4, p0[2] + dir * (1.2 + hash(s.seed + 4) * 1.8)];
  const t0 = [base.t[0] + h3 * .8, base.t[1] + h1 * .5, base.t[2]];
  const t1 = [t0[0] + h1 * 1.2, t0[1] + h2 * .6, t0[2] + h3 * .8];
  return { p0, p1, t0, t1 };
}
const CACHE = new Map();
function getCam(s) {
  if (!CACHE.has(s.seed)) CACHE.set(s.seed, camFor(s));
  return CACHE.get(s.seed);
}
function shotAt(t) {
  for (let i = 0; i < SHOTS.length; i++) if (t < SHOTS[i].b) return SHOTS[i];
  return SHOTS[SHOTS.length - 1];
}

function textLines(text, x, y, maxW, lineH, font, color, stroke) {
  g.font = font; g.textAlign = 'center'; g.textBaseline = 'middle';
  const words = text.split(' '), lines = []; let cur = '';
  for (const w of words) {
    const test = cur ? cur + ' ' + w : w;
    if (g.measureText(test).width > maxW && cur) { lines.push(cur); cur = w; }
    else cur = test;
  }
  if (cur) lines.push(cur);
  lines.forEach((line, i) => {
    const yy = y + (i - (lines.length - 1) / 2) * lineH;
    g.lineWidth = 10; g.strokeStyle = stroke; g.strokeText(line, x, yy);
    g.fillStyle = color; g.fillText(line, x, yy);
  });
}

function overlay(t, s) {
  const u = clamp((t - s.a) / (s.b - s.a));
  g.save(); g.setTransform(1, 0, 0, 1, 0, 0);
  const vg = g.createRadialGradient(W/2, H*.45, H*.22, W/2, H*.5, H*.72);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(2,5,14,0.42)');
  g.fillStyle = vg; g.fillRect(0, 0, W, H);
  g.fillStyle = 'rgba(7,11,24,0.62)'; g.fillRect(0, 0, W, 72);
  g.fillStyle = '#ffd166'; g.font = '700 27px Fredoka, Arial, sans-serif';
  g.textAlign = 'left'; g.textBaseline = 'middle';
  g.fillText('A STORY', 42, 36);
  g.fillStyle = '#dff3ff'; g.textAlign = 'right'; g.fillText('SHORTS', W - 42, 36);
  if (u < .44) {
    g.globalAlpha = 1 - u / .44;
    g.fillStyle = 'rgba(6,10,22,0.72)'; g.fillRect(0, H*.20, W, 150);
    textLines(s.title, W/2, H*.20 + 75, W - 110, 66,
      '800 66px Fredoka, Arial Black, sans-serif', '#ffffff', '#0a1020');
    g.globalAlpha = 1;
  }
  g.fillStyle = 'rgba(6,10,22,0.74)'; g.fillRect(48, H - 310, W - 96, 190);
  g.fillStyle = '#ffd166'; g.fillRect(48, H - 310, 10, 190);
  textLines(s.caption, W/2, H - 215, W - 160, 68,
    '700 56px Fredoka, Arial, sans-serif', '#ffffff', '#070b18');
  g.fillStyle = 'rgba(255,255,255,0.20)'; g.fillRect(48, H - 92, W - 96, 8);
  g.fillStyle = '#ffd166'; g.fillRect(48, H - 92, (W - 96) * u, 8);
  g.restore();
}

window.renderOut = function (t) {
  t = clamp(+t || 0, 0, DUR);
  const s = shotAt(t), cam = getCam(s);
  const u = clamp((t - s.a) / (s.b - s.a)), e = ease(u);

  for (const m of meshes) m.visible = (m.userData.part.g === s.beat);

  const pos = new THREE.Vector3(
    lerp(cam.p0[0], cam.p1[0], e) + Math.sin(t * 5.1 + s.seed) * .07,
    lerp(cam.p0[1], cam.p1[1], e) + Math.sin(t * 3.7 + s.seed) * .05,
    lerp(cam.p0[2], cam.p1[2], e));
  const tgt = new THREE.Vector3(lerp(cam.t0[0], cam.t1[0], e),
    lerp(cam.t0[1], cam.t1[1], e), lerp(cam.t0[2], cam.t1[2], e));
  camera.position.copy(pos);
  camera.up.set(Math.sin(t * 1.3 + s.seed) * .025, 1, 0);
  camera.lookAt(tgt);

  const swing = Math.sin(t * 8 + s.seed * .2);
  for (const m of meshes) {
    if (!m.visible) continue;
    const p = m.userData.part, nm = p.n;
    if (nm.startsWith('prop_')) m.rotation.y += 0; // props stay still; camera does the work
    if (p.role === 'hero' || p.role === 'shadow' || p.role.startsWith('crowd')) {
      m.position.y = m.userData.baseY + Math.abs(swing) * .055;
      if (/_armL$/.test(nm)) m.rotation.z = m.userData.baseZ + swing * .32;
      if (/_armR$/.test(nm)) m.rotation.z = m.userData.baseZ - swing * .32;
      if (/_legL$/.test(nm)) m.rotation.z = m.userData.baseZ - swing * .22;
      if (/_legR$/.test(nm)) m.rotation.z = m.userData.baseZ + swing * .22;
    }
  }

  renderer.render(scene, camera);
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.clearRect(0, 0, W, H);
  g.drawImage(glCanvas, 0, 0, W, H);
  overlay(t, s);
};

(async () => {
  try { await document.fonts.ready; } catch (e) {}
  window.renderOut(0);
  window.READY = true;
})();
