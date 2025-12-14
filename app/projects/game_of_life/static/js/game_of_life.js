const BASE_URL = window.GOL_BASE_URL || "/projects/game_of_life/";

let running = false;
let intervalId = null;

async function fetchJson(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
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
  // ⬇️ Ici, les éléments existent enfin

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
    running = false;
    if (intervalId) clearInterval(intervalId);
    intervalId = null;
  });

  document.getElementById('reset').addEventListener('click', async () => {
    running = false;
    if (intervalId) clearInterval(intervalId);
    intervalId = null;

    await fetchJson(`${BASE_URL}reset`, { method: 'POST' });
    const data = await fetchJson(`${BASE_URL}state`);
    drawGrid(data.grid);
  });

  document.getElementById('clear').addEventListener('click', async () => {
    running = false;
    if (intervalId) clearInterval(intervalId);
    intervalId = null;

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

    // ⚠️ ton code appelait refreshPatternList() (qui n’existe pas)
    await refreshSavedPatterns();
  });

  document.getElementById('load-pattern').addEventListener('click', async () => {
    running = false;
    if (intervalId) clearInterval(intervalId);
    intervalId = null;

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

  // Initialisation
  (async () => {
    await refreshSavedPatterns();
    const data = await fetchJson(`${BASE_URL}state`);
    drawGrid(data.grid);
  })();
});
