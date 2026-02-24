const BASE_URL = window.GOL_BASE_URL || "/projects/game_of_life/";

let running = false;
let intervalId = null;

// ✅ anti-race token
let drawVersion = 0;

async function fetchJson(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

// ✅ dessine seulement si c’est la réponse la plus récente
async function safeFetchAndDraw(fetchPromise) {
  const version = ++drawVersion;      // invalide toutes les requêtes précédentes
  const data = await fetchPromise;
  if (version !== drawVersion) return; // réponse obsolète => ignore
  drawGrid(data.grid);
  return data; // utile si tu veux lire data.rows/cols plus tard
}

function stopRunning() {
  running = false;
  if (intervalId) clearInterval(intervalId);
  intervalId = null;
}

function autoGridSize() {
  const w = window.innerWidth;
  if (w < 640) return { rows: 30, cols: 30 };
  if (w < 1024) return { rows: 60, cols: 60 };
  return { rows: 60, cols: 60 };
}

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

  await safeFetchAndDraw(
    fetchJson(`${BASE_URL}grid`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rows, cols })
    })
  );
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
  await safeFetchAndDraw(fetchJson(`${BASE_URL}next`));
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
  document.getElementById('grid-container').addEventListener('click', async (event) => {
    const cell = event.target.closest("td.cell");
    if (!cell) return;
    if (running) return;

    const row = cell.dataset.row;
    const col = cell.dataset.col;

    await safeFetchAndDraw(
      fetchJson(`${BASE_URL}toggle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ row, col })
      })
    );
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
    await safeFetchAndDraw(fetchJson(`${BASE_URL}state`));
  });

  document.getElementById('clear').addEventListener('click', async () => {
    stopRunning();
    await fetchJson(`${BASE_URL}clear`, { method: 'POST' });
    await safeFetchAndDraw(fetchJson(`${BASE_URL}state`));
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

    if (kind === 'gen') {
      await safeFetchAndDraw(
        fetchJson(`${BASE_URL}pattern`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name })
        })
      );
    } else if (kind === 'saved') {
      await safeFetchAndDraw(
        fetchJson(`${BASE_URL}load`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name })
        })
      );
    } else {
      alert('Type de pattern inconnu.');
      return;
    }
  });

  const gridSizeSelect = document.getElementById('grid-size');
  const applyGridBtn = document.getElementById('apply-grid');

  if (gridSizeSelect && applyGridBtn) {
    applyGridBtn.addEventListener('click', async () => {
      await applyGridSize(gridSizeSelect.value);
    });
  }

  (async () => {
    await refreshSavedPatterns();
    await safeFetchAndDraw(fetchJson(`${BASE_URL}state`));
  })();
});