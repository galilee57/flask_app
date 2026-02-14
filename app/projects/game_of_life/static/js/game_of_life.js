const BASE_URL = window.GOL_BASE_URL || "/projects/game_of_life/";

let running = false;
let intervalId = null;

async function fetchJson(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

function stopRunning() {
  running = false;
  if (intervalId) clearInterval(intervalId);
  intervalId = null;
}

function autoGridSize() {
  // Breakpoints simples (à ajuster)
  const w = window.innerWidth;
  if (w < 640) return { rows: 40, cols: 40 };
  if (w < 1024) return { rows: 60, cols: 60 };
  return { rows: 60, cols: 60 };
}

/**
 * ⚠️ Nécessite une route backend:
 * POST `${BASE_URL}grid` avec body {rows, cols}
 * -> renvoie { grid: [...] }
 */
async function applyGridSize(value) {
  stopRunning();

  let rows, cols;
  if (value === "auto") {
    ({ rows, cols } = autoGridSize());
  } else {
    const [r, c] = value.split("x").map(Number);
    rows = r;
    cols = c;
  }

  const data = await fetchJson(`${BASE_URL}grid`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rows, cols })
  });

  drawGrid(data.grid);
}

function drawGrid(grid) {
  const gridDiv = document.getElementById("grid-container");
  let html = "<table id='gol-grid'>";
  for (let r = 0; r < grid.length; r++) {
    html += "<tr>";
    for (let c = 0; c < grid[r].length; c++) {
      const cell = grid[r][c];
      html += `<td class="cell ${cell ? 'alive' : ''}" data-row="${r}" data-col="${c}"></td>`;
    }
    html += "</tr>";
  }
  html += "</table>";
  gridDiv.innerHTML = html;
}

async function updateGrid() {
  const data = await fetchJson(`${BASE_URL}next`);
  drawGrid(data.grid);
}

async function refreshSavedPatterns() {
  const data = await fetchJson(`${BASE_URL}saved`);
  const saved = data.patterns || [];
  const group = document.getElementById('saved-optgroup');
  if (!group) return;
  group.innerHTML = '';
  for (const name of saved) {
    const opt = document.createElement('option');
    opt.value = `saved:${name}`;
    opt.textContent = name;
    group.appendChild(opt);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // Clic sur la grille
  document.getElementById('grid-container').addEventListener('click', async (event) => {
    const cell = event.target.closest("td.cell");
    if (!cell) return;
    if (running) return;

    const row = cell.dataset.row;
    const col = cell.dataset.col;

    const data = await fetchJson(`${BASE_URL}toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ row, col })
    });
    drawGrid(data.grid);
  });

  document.getElementById('start').addEventListener('click', () => {
    if (!running) {
      running = true;
      intervalId = setInterval(updateGrid, 500);
    }
  });

  document.getElementById('stop').addEventListener('click', () => {
    stopRunning();
  });

  document.getElementById('reset').addEventListener('click', async () => {
    stopRunning();

    await fetchJson(`${BASE_URL}reset`, { method: 'POST' });
    const data = await fetchJson(`${BASE_URL}state`);
    drawGrid(data.grid);
  });

  document.getElementById('clear').addEventListener('click', async () => {
    stopRunning();

    await fetchJson(`${BASE_URL}clear`, { method: 'POST' });
    const data = await fetchJson(`${BASE_URL}state`);
    drawGrid(data.grid);
  });

  document.getElementById('save-pattern').addEventListener('click', async () => {
    const input = document.getElementById('pattern-name');
    const name = input.value.trim();
    if (!name) {
      alert('Donne un nom au pattern 🙂');
      return;
    }

    await fetchJson(`${BASE_URL}save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });

    await refreshSavedPatterns();
  });

  document.getElementById('load-pattern').addEventListener('click', async () => {
    stopRunning();

    const select = document.getElementById('pattern-select');
    const value = select.value;
    if (!value) {
      alert('Choisis un pattern à charger.');
      return;
    }

    const [kind, name] = value.split(':');
    let data;

    if (kind === 'gen') {
      data = await fetchJson(`${BASE_URL}pattern`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });
    } else if (kind === 'saved') {
      data = await fetchJson(`${BASE_URL}load`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });
    } else {
      alert('Type de pattern inconnu.');
      return;
    }

    drawGrid(data.grid);
  });

  // ✅ Bouton / select pour changer la grille
  // Attendus dans ton HTML:
  // - <select id="grid-size"> avec values: auto, 40x40, 60x60, ...
  // - <button id="apply-grid">
  const gridSizeSelect = document.getElementById('grid-size');
  const applyGridBtn = document.getElementById('apply-grid');

  if (gridSizeSelect && applyGridBtn) {
    applyGridBtn.addEventListener('click', async () => {
      await applyGridSize(gridSizeSelect.value);
    });

    // Optionnel: double-clic ou Enter = appliquer direct
    gridSizeSelect.addEventListener('change', async () => {
      // décommente si tu veux appliquer automatiquement au changement
      // await applyGridSize(gridSizeSelect.value);
    });
  }

  // Initialisation
  (async () => {
    await refreshSavedPatterns();

    // Optionnel: si tu veux démarrer avec une taille "Auto" au lieu du state backend actuel
    // (sinon laisse comme avant)
    // if (gridSizeSelect && gridSizeSelect.value === 'auto') {
    //   await applyGridSize('auto');
    //   return;
    // }

    const data = await fetchJson(`${BASE_URL}state`);
    drawGrid(data.grid);
  })();
});
