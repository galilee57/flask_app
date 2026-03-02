// app/projects/viewer360/static/js/projet_360viewer.js

console.log("projet_360viewer.js chargé");

const holder    = document.getElementById("canvas-holder");
const loadingEl = document.getElementById("loading");
const selectEl  = document.getElementById("select");
const gridEl    = document.getElementById("grid");

// ---------- THREE en global (UMD) ----------
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, 2, 0.1, 2000);
camera.position.set(0, 0, 0.1);

const renderer = new THREE.WebGLRenderer({ antialias: true });
holder.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableZoom = false;
controls.enablePan = false;
controls.enableDamping = true;
controls.dampingFactor = 0.05;

function setSize() {
  const w = holder.clientWidth;
  const h = holder.clientHeight;
  renderer.setSize(w, h, false);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  console.log("holder size:", w, h);
}
window.addEventListener("resize", setSize);
setSize();

// 🔥 Fix: si le layout Tailwind finit de se calculer après le chargement,
// ton holder peut être à 0x0 lors du 1er setSize() -> canvas invisible.
const ro = new ResizeObserver(() => setSize());
ro.observe(holder);

// Et un petit "kick" au prochain frame
requestAnimationFrame(() => setSize());
setTimeout(() => setSize(), 50);

const radius = 500;
const geometry = new THREE.SphereGeometry(radius, 64, 32);
geometry.scale(-1, 1, 1);

let material = new THREE.MeshBasicMaterial({ color: 0x000000 });
let mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);

const manager = new THREE.LoadingManager();
const loader = new THREE.TextureLoader(manager);

manager.onStart = () => { loadingEl.style.display = "block"; };
manager.onLoad  = () => { loadingEl.style.display = "none"; };

let currentTexture = null;

function loadTexture(url) {
  loadingEl.style.display = "block";

  loader.load(
    url,
    (texture) => {
      if ("colorSpace" in texture && THREE.SRGBColorSpace) {
        texture.colorSpace = THREE.SRGBColorSpace;
      } else if ("encoding" in texture && THREE.sRGBEncoding) {
        texture.encoding = THREE.sRGBEncoding;
      }

      if (currentTexture) currentTexture.dispose();
      currentTexture = texture;

      mesh.material.map = texture;
      mesh.material.needsUpdate = true;

      loadingEl.style.display = "none";
    },
    undefined,
    (err) => {
      console.error(err);
      loadingEl.textContent = "Erreur de chargement 😕";
    }
  );
}

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();

renderer.domElement.addEventListener(
  "touchmove",
  (e) => e.preventDefault(),
  { passive: false }
);

// ---------- API images -> UI ----------
async function populateFromAPI() {
  try {
    const res = await fetch(API_IMAGES_URL, { cache: "no-store" });
    const data = await res.json();
    const items = data.items || [];

    selectEl.innerHTML = "";
    gridEl.innerHTML = "";

    items.forEach((it) => {
      const opt = document.createElement("option");
      opt.value = it.url;
      opt.textContent = it.name;
      selectEl.appendChild(opt);

      const card = document.createElement("div");
      card.className = "thumb relative cursor-pointer rounded-lg hover:ring-indigo-500 hover:ring-offset-2 hover:ring-offset-white overflow-hidden transition-all duration-200";
      card.dataset.url = it.url;   // 👈 important pour identifier la card
      card.onclick = () => {
        selectEl.value = it.url;
        loadTexture(it.url);
        setActiveCard(it.url);
      };

      const img = document.createElement("img");
      img.src = it.url;
      img.loading = "lazy";

      const label = document.createElement("div");
      label.className = "label";
      //label.textContent = it.name;

      card.appendChild(img);
      card.appendChild(label);
      gridEl.appendChild(card);
    });

    if (items[0]) {
      selectEl.value = items[0].url;
      loadTexture(items[0].url);
    } else {
      loadingEl.textContent = "Aucune image trouvée";
    }
  } catch (err) {
    console.error(err);
    loadingEl.textContent = "Erreur API images";
  }
}

function setActiveCard(url) {
  const allCards = document.querySelectorAll(".thumb");

  allCards.forEach(card => {
    if (card.dataset.url === url) {
      card.classList.add("ring-2", "ring-indigo-500", "ring-offset-2", "ring-offset-white");
    } else {
      card.classList.remove("ring-2", "ring-indigo-500", "ring-offset-2", "ring-offset-white");
    }
  });
}

selectEl.addEventListener("change", (e) => {
  const url = e.target.value;
  if (url) loadTexture(url);
});

populateFromAPI();
