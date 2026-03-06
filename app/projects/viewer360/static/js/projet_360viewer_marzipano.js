console.log("projet_360viewer_marzipano.js chargé");

const panoEl = document.getElementById("pano");
const loadingEl = document.getElementById("loading");
const selectEl = document.getElementById("select");
const gridEl = document.getElementById("grid");

// --- Marzipano viewer (exemple minimal)
const viewer = new Marzipano.Viewer(panoEl, { controls: { mouseViewMode: "drag" } });

function createEquirectScene(url) {
  const source = Marzipano.ImageUrlSource.fromString(url);
  const geometry = new Marzipano.EquirectGeometry([{ width: 8000 }]); // ajuste (4000/6000/8000)
  const limiter = Marzipano.RectilinearView.limit.traditional(1024, (100 * Math.PI) / 180);
  const view = new Marzipano.RectilinearView({ yaw: 0, pitch: 0, fov: (75 * Math.PI) / 180 }, limiter);
  return viewer.createScene({ source, geometry, view, pinFirstLevel: true });
}

let currentScene = null;

function switchToImage(url) {
  loadingEl.style.display = "block";
  const scene = createEquirectScene(url);
  scene.switchTo({ transitionDuration: 200 });
  currentScene = scene;

  requestAnimationFrame(() => {
    loadingEl.style.display = "none";
  });
}

// --- UI helpers
function setActiveCard(url) {
  gridEl.querySelectorAll("[data-url]").forEach((card) => {
    if (card.dataset.url === url) {
      card.classList.add("ring-2", "ring-indigo-500", "ring-offset-2", "ring-offset-white");
    } else {
      card.classList.remove("ring-2", "ring-indigo-500", "ring-offset-2", "ring-offset-white");
    }
  });
}

function makeThumbCard(it) {
  // bouton (cliquable) avec taille explicite => jamais invisible
  const card = document.createElement("button");
  card.type = "button";
  card.dataset.url = it.url;

  card.className = [
    "relative",
    "h-20",               // hauteur fixée
    "w-full",             // prend toute la colonne de la grille
    "overflow-hidden",
    "rounded-lg",
    "border",
    "border-gray-200",
    "bg-gray-100",
    "shadow-sm",
    "transition",
    "hover:shadow",
    "focus:outline-none",
    "focus:ring-2",
    "focus:ring-indigo-500/40"
  ].join(" ");

  const img = document.createElement("img");
  img.src = it.url;           // simple: on réutilise l’image
  img.alt = it.name;
  img.loading = "lazy";
  img.decoding = "async";
  img.className = "h-full w-full object-cover";

  img.onerror = () => {
    card.innerHTML = `<div class="flex h-full w-full items-center justify-center text-xs text-gray-500">thumb error</div>`;
  };

  const label = document.createElement("div");
  label.className = "pointer-events-none absolute bottom-1 left-1 right-1 truncate rounded bg-black/40 px-1.5 py-0.5 text-[10px] text-white";
  label.textContent = it.name;

  card.appendChild(img);
  card.appendChild(label);

  return card;
}

// --- Populate
async function populateFromAPI() {
  try {
    console.log("API_IMAGES_URL =", API_IMAGES_URL);

    const res = await fetch(API_IMAGES_URL, { cache: "no-store" });
    console.log("API status =", res.status);

    const data = await res.json();
    const items = data.items || [];
    console.log("items =", items);

    selectEl.innerHTML = "";
    gridEl.innerHTML = "";

    items.forEach((it) => {
      // select
      const opt = document.createElement("option");
      opt.value = it.url;
      opt.textContent = it.name;
      selectEl.appendChild(opt);

      // thumbs
      const card = makeThumbCard(it);
      card.addEventListener("click", () => {
        selectEl.value = it.url;
        switchToImage(it.url);
        setActiveCard(it.url);
      });
      gridEl.appendChild(card);
    });

    if (items[0]) {
      selectEl.value = items[0].url;
      switchToImage(items[0].url);
      setActiveCard(items[0].url);
    } else {
      loadingEl.textContent = "Aucune image trouvée";
    }
  } catch (e) {
    console.error(e);
    loadingEl.textContent = "Erreur API images";
  }
}

selectEl.addEventListener("change", (e) => {
  const url = e.target.value;
  if (url) {
    switchToImage(url);
    setActiveCard(url);
  }
});

populateFromAPI();