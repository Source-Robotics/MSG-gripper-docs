/* The gripper configurator: a three.js view of the model that tools/build_model.py writes (body.glb, one
   jaws_<option>.glb per finger option, viewer.json). A model without jaws and colours (the driver boards) is
   shown as it is: turn and zoom only. The reader turns and zooms the gripper, opens and closes
   the jaws, picks the fingers and the colours of the body and the fingers. Loaded as a module by
   gripper-viewer-loader.js only on a page that has a .gripper-viewer element; three.js comes from the import
   map in overrides/main.html. */
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

async function mount(el) {
  if (el.dataset.ready) return;
  el.dataset.ready = "1";
  const base = new URL(el.dataset.base, window.location.href).href;
  const cfg = await (await fetch(base + "viewer.json")).json();
  const canvas = el.querySelector("canvas");
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.1;
  const scene = new THREE.Scene();
  scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
  const camera = new THREE.PerspectiveCamera(35, 1, 0.005, 10);
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 1.2;
  controls.addEventListener("start", () => { controls.autoRotate = false; });
  const root = new THREE.Group();
  scene.add(root);
  const loader = new GLTFLoader();
  const load = (file) => new Promise((ok, err) => loader.load(base + file, (g) => ok(g.scene), undefined, err));

  const state = { body: null, jaws: null, jawNodes: {}, colors: { ...cfg.default }, opening: cfg.default.opening };
  const dirs = cfg.dir ? { jaw1: new THREE.Vector3().fromArray(cfg.dir.jaw1), jaw2: new THREE.Vector3().fromArray(cfg.dir.jaw2) } : null;

  function paint(obj, hex) {
    if (!obj) return;
    obj.traverse((o) => {
      if (o.isMesh) {
        if (!o.userData.own) { o.material = o.material.clone(); o.userData.own = true; }
        o.material.color.set(hex);
      }
    });
  }
  function applyOpening() {
    if (!dirs) return;
    for (const name of ["jaw1", "jaw2"]) {
      const n = state.jawNodes[name];
      if (n) n.position.copy(dirs[name]).multiplyScalar(cfg.travel_m * state.opening);
    }
  }
  function frame() {
    const box = new THREE.Box3().setFromObject(root);
    const size = box.getSize(new THREE.Vector3()).length();
    const centre = box.getCenter(new THREE.Vector3());
    const dist = (size / 2) / Math.tan((camera.fov * Math.PI) / 360) * (cfg.camera.fill || 1.25);
    const az = (cfg.camera.azimuth_deg * Math.PI) / 180, po = (cfg.camera.polar_deg * Math.PI) / 180;
    camera.position.set(centre.x + dist * Math.sin(po) * Math.sin(az), centre.y + dist * Math.cos(po), centre.z + dist * Math.sin(po) * Math.cos(az));
    controls.target.copy(centre);
    controls.update();
  }
  async function setJaws(key) {
    const opt = cfg.jaws.find((j) => j.key === key) || cfg.jaws[0];
    const next = await load(opt.file);
    if (state.jaws) root.remove(state.jaws);
    state.jaws = next;
    state.jawNodes = { jaw1: next.getObjectByName("jaw1"), jaw2: next.getObjectByName("jaw2") };
    root.add(next);
    paint(next, state.colors.jaws_color);
    applyOpening();
  }

  state.body = await load(cfg.body);
  root.add(state.body);
  if (state.colors.body) paint(state.body, state.colors.body);   // a model with its own colours (a board) is left as it is
  if (cfg.jaws && cfg.jaws.length) await setJaws(cfg.default.jaws);
  frame();

  // the controls
  const q = (n) => el.querySelector("[name=" + n + "]");
  const opening = q("opening");
  if (opening) { opening.value = Math.round(state.opening * 100); opening.addEventListener("input", () => { state.opening = opening.value / 100; applyOpening(); }); }
  const select = q("jaws");
  if (select) {
    select.innerHTML = cfg.jaws.map((j) => `<option value="${j.key}"${j.key === cfg.default.jaws ? " selected" : ""}>${j.label}</option>`).join("");
    select.addEventListener("change", () => setJaws(select.value));
  }
  for (const target of ["body", "jaws"]) {
    const input = q(target === "body" ? "body" : "jaws_color");
    const key = target === "body" ? "body" : "jaws_color";
    const swatches = el.querySelector(`.gripper-viewer__swatches[data-target="${target}"]`);
    const apply = (hex) => { state.colors[key] = hex; paint(target === "body" ? state.body : state.jaws, hex); if (input) input.value = hex; };
    if (swatches) {
      for (const [name, hex] of Object.entries(cfg.colors[target] || {})) {
        const b = document.createElement("button");
        b.type = "button"; b.title = name; b.setAttribute("aria-label", name);
        b.style.background = hex;
        b.addEventListener("click", () => apply(hex));
        swatches.appendChild(b);
      }
    }
    if (input) { input.value = state.colors[key]; input.addEventListener("input", () => apply(input.value)); }
  }
  const reset = q("reset");
  if (reset) reset.addEventListener("click", () => { frame(); controls.autoRotate = true; });

  // size, visibility, render
  const resize = () => {
    const w = el.clientWidth || canvas.clientWidth, h = canvas.clientHeight || Math.round(w * 0.62);
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  };
  new ResizeObserver(resize).observe(el);
  resize();
  let visible = true;
  new IntersectionObserver((e) => { visible = e[0].isIntersecting; }).observe(el);
  renderer.setAnimationLoop(() => { if (!visible) return; controls.update(); renderer.render(scene, camera); });
}

document.querySelectorAll(".gripper-viewer").forEach((el) => mount(el).catch((e) => {
  console.error("gripper viewer:", e);
  const hint = el.querySelector(".gripper-viewer__hint");
  if (hint) hint.textContent = "The 3D view could not load in this browser.";
}));
