import * as THREE from './three.module.js';

// The world comes from src/roblox_place.py as scene.js. This file only frames,
// lights and animates those parts. Pure function of t: no clock, no state.
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
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xbfefff);
scene.fog = new THREE.Fog(0xbfefff, 38, 130);

const camera = new THREE.PerspectiveCamera(44, W / H, 0.1, 250);

// Bright studio lighting: no moody navy, no dark vignette.
scene.add(new THREE.HemisphereLight(0xffffff, 0x9fd8ff, 2.0));
const key = new THREE.DirectionalLight(0xfff6df, 1.45);
key.position.set(7, 16, 11); scene.add(key);
const fill = new THREE.DirectionalLight(0x9fd8ff, 0.85);
fill.position.set(-9, 7, 6); scene.add(fill);
const rim = new THREE.DirectionalLight(0xffffff, 0.6);
rim.position.set(0, 8, -12); scene.add(rim);

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
  Ball: new THREE.SphereGeometry(0.5, 16, 12),
  Cylinder: new THREE.CylinderGeometry(0.5, 0.5, 1, 12)
};
const EDGE_BOX = new THREE.EdgesGeometry(GEO.Box);
const EDGE_MAT = new THREE.LineBasicMaterial({ color: 0x26374f, transparent: true, opacity: 0.42 });

const matCache = new Map();
function material(c) {
  const hex = ((c[0] << 16) | (c[1] << 8) | c[2]);
  if (!matCache.has(hex)) {
    matCache.set(hex, new THREE.MeshLambertMaterial({ color: hex, flatShading: true }));
  }
  return matCache.get(hex);
}

const meshes = [];
PARTS.forEach((p, i) => {
  const m = new THREE.Mesh(GEO[p.sh] || GEO.Box, material(p.c));
  m.position.set(p.p[0], p.p[1], p.p[2]);
  m.scale.set(p.s[0], p.s[1], p.s[2]);
  m.rotation.set(p.r[0], p.r[1], p.r[2], 'ZYX');
  m.userData = {
    part: p, i,
    baseX: p.p[0], baseY: p.p[1], baseZ: p.p[2],
    baseRX: p.r[0], baseRY: p.r[1], baseRZ: p.r[2]
  };
  // Crisp outlines only on the things the eye follows: people and props.
  if (p.sh === 'Box' && (p.role === 'hero' || p.role === 'anya' || p.role === 'shadow' ||
      String(p.role).startsWith('crowd') || p.role === 'prop' || p.n.startsWith('prop_'))) {
    const edge = new THREE.LineSegments(EDGE_BOX, EDGE_MAT);
    edge.scale.set(1.004, 1.004, 1.004);
    m.add(edge);
  }
  scene.add(m); meshes.push(m);
});

// ~1.1s cuts, matching the Gneef pace.
const SHOT_LEN = 1.12;
const SHOTS = [];
BEATS.forEach((b, bi) => {
  const len = Math.max(0.5, b.t1 - b.t0);
  const count = Math.max(1, Math.ceil(len / SHOT_LEN));
  for (let j = 0; j < count; j++) {
    SHOTS.push({
      a: b.t0 + len * j / count,
      b: b.t0 + len * (j + 1) / count,
      beat: bi,
      beatStart: b.t0,
      part: j,
      count,
      caption: b.caption,
      title: b.title,
      move: b.move || 'push',
      seed: bi * 97 + j
    });
  }
});
window.SF_SHOTS = SHOTS;

// Close, low cameras: the blocky character and the prop fill the frame.
const CAMS = [
  { p: [4.6, 3.0, 7.2],  t: [-0.8, 2.15, 0.6] },
  { p: [-3.8, 2.9, 6.9], t: [0.2, 2.05, -1.0] },
  { p: [0.4, 5.0, 8.3],  t: [0.0, 1.75, -3.2] },
  { p: [5.4, 3.5, 5.8],  t: [-0.2, 2.0, -2.4] },
  { p: [-5.0, 2.7, 5.9], t: [-1.0, 2.1, 1.1] },
  { p: [1.8, 2.6, 6.4],  t: [-1.6, 2.2, 0.8] },
  { p: [3.2, 4.2, 7.6],  t: [0.0, 1.9, -1.6] },
  { p: [-1.8, 3.1, 7.8], t: [-0.5, 2.05, -0.2] }
];
function camFor(s) {
  const base = CAMS[s.seed % CAMS.length];
  const h1 = hash(s.seed + 1) - .5, h2 = hash(s.seed + 2) - .5, h3 = hash(s.seed + 3) - .5;
  const p0 = [base.p[0] + h1 * 1.1, base.p[1] + h2 * 0.5, base.p[2] + h3 * 0.8];
  const dir = s.move === 'pull' ? 1 : -1;
  const p1 = [p0[0] + h2 * 1.3, p0[1] + h3 * 0.5, p0[2] + dir * (0.7 + hash(s.seed + 4) * 0.8)];
  const t0 = [base.t[0] + h3 * 0.35, base.t[1] + h1 * 0.25, base.t[2]];
  const t1 = [t0[0] + h1 * 0.45, t0[1] + h2 * 0.25, t0[2] + h3 * 0.35];
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

function roundRect(x, y, w, h, r) {
  g.beginPath();
  g.moveTo(x + r, y);
  g.arcTo(x + w, y, x + w, y + h, r);
  g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r);
  g.arcTo(x, y, x + w, y, r);
  g.closePath();
}
function textLines(text, x, y, maxW, lineH, font, color, stroke) {
  g.font = font; g.textAlign = 'center'; g.textBaseline = 'middle';
  const words = String(text || '').split(' '), lines = []; let cur = '';
  for (const w of words) {
    const test = cur ? cur + ' ' + w : w;
    if (g.measureText(test).width > maxW && cur) { lines.push(cur); cur = w; }
    else cur = test;
  }
  if (cur) lines.push(cur);
  lines.forEach((line, i) => {
    const yy = y + (i - (lines.length - 1) / 2) * lineH;
    if (stroke) { g.lineWidth = 7; g.strokeStyle = stroke; g.strokeText(line, x, yy); }
    g.fillStyle = color; g.fillText(line, x, yy);
  });
}

function overlay(t, s) {
  const u = clamp((t - s.a) / (s.b - s.a));
  g.save(); g.setTransform(1, 0, 0, 1, 0, 0);

  // Very light vignette; the world stays bright.
  const vg = g.createRadialGradient(W/2, H*.42, H*.28, W/2, H*.5, H*.78);
  vg.addColorStop(0, 'rgba(0,0,0,0)');
  vg.addColorStop(1, 'rgba(12,32,58,0.16)');
  g.fillStyle = vg; g.fillRect(0, 0, W, H);

  // Small clean brand pills.
  g.fillStyle = 'rgba(255,255,255,0.92)';
  roundRect(34, 30, 170, 54, 18); g.fill();
  g.fillStyle = '#233b5b'; g.font = '800 25px Fredoka, Arial, sans-serif';
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText('A STORY', 119, 58);
  g.fillStyle = 'rgba(255,255,255,0.92)';
  roundRect(W - 194, 30, 160, 54, 18); g.fill();
  g.fillStyle = '#233b5b'; g.fillText('SHORTS', W - 114, 58);

  // Beat title, only at the start of each 4-second story beat.
  if (t - s.beatStart < 0.42) {
    g.globalAlpha = 1 - (t - s.beatStart) / 0.42;
    g.fillStyle = 'rgba(255,209,102,0.96)';
    roundRect(W/2 - 300, H*.17, 600, 92, 26); g.fill();
    textLines(s.title, W/2, H*.17 + 46, 550, 60,
      '900 46px Fredoka, Arial Black, sans-serif', '#233b5b');
    g.globalAlpha = 1;
  }

  // Big readable caption card, white plastic with a yellow edge.
  const boxY = H - 346;
  g.fillStyle = 'rgba(255,255,255,0.96)';
  roundRect(40, boxY, W - 80, 226, 30); g.fill();
  g.fillStyle = '#ffd166';
  roundRect(40, boxY, 14, 226, 7); g.fill();
  textLines(s.caption, W/2, boxY + 106, W - 170, 72,
    '800 58px Fredoka, Arial Black, sans-serif', '#1e3050');

  // Progress bar.
  g.fillStyle = 'rgba(255,255,255,0.55)';
  roundRect(48, H - 88, W - 96, 10, 5); g.fill();
  g.fillStyle = '#ffd166';
  roundRect(48, H - 88, (W - 96) * u, 10, 5); g.fill();
  g.restore();
}

window.renderOut = function (t) {
  t = clamp(+t || 0, 0, DUR);
  const s = shotAt(t), cam = getCam(s);
  const u = clamp((t - s.a) / (s.b - s.a)), e = ease(u);

  for (const m of meshes) m.visible = (m.userData.part.g === s.beat);

  const pos = new THREE.Vector3(
    lerp(cam.p0[0], cam.p1[0], e) + Math.sin(t * 5.1 + s.seed) * .04,
    lerp(cam.p0[1], cam.p1[1], e) + Math.sin(t * 3.7 + s.seed) * .035,
    lerp(cam.p0[2], cam.p1[2], e));
  const tgt = new THREE.Vector3(
    lerp(cam.t0[0], cam.t1[0], e),
    lerp(cam.t0[1], cam.t1[1], e),
    lerp(cam.t0[2], cam.t1[2], e));
  camera.position.copy(pos);
  camera.up.set(Math.sin(t * 1.1 + s.seed) * .012, 1, 0);
  camera.lookAt(tgt);

  const swing = Math.sin(t * 9 + s.seed * .37);
  for (const m of meshes) {
    if (!m.visible) continue;
    const d = m.userData, p = d.part, nm = p.n, role = p.role || '';
    // Reset every animated channel from the manifest: no accumulated drift.
    m.position.set(d.baseX, d.baseY, d.baseZ);
    m.rotation.set(d.baseRX, d.baseRY, d.baseRZ, 'ZYX');

    if (role === 'hero' || role === 'anya' || role === 'shadow' || String(role).startsWith('crowd')) {
      m.position.y = d.baseY + Math.abs(swing) * .07;
      if (/_armL$/.test(nm)) m.rotation.z = d.baseRZ + swing * .38;
      if (/_armR$/.test(nm)) m.rotation.z = d.baseRZ - swing * .38;
      if (/_legL$/.test(nm)) m.rotation.z = d.baseRZ - swing * .24;
      if (/_legR$/.test(nm)) m.rotation.z = d.baseRZ + swing * .24;
    } else if (role === 'prop' || nm.startsWith('prop_')) {
      m.position.y = d.baseY + Math.abs(Math.sin(t * 5.4 + s.seed)) * .12;
      m.rotation.y = d.baseRY + Math.sin(t * 3.1 + s.seed) * .14;
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
