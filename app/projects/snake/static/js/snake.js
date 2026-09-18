const canvas = document.getElementById("game-canvas");
const ctx = canvas.getContext("2d");

// --- BOARD DEFINITION ---

const GRID_W = 20;
const GRID_H = 20;

const TILE_W = 64;
const TILE_H = 32;

let fruit = null;
let snake = [];
let currentDirection = "right";
let gameLoop = null;
let isMoving = false;
let finishedGame = null;
let movementPromise = null;
let isResetting = false;
let statsLoading = false;
let loopGeneration = 0;

function resizeCanvas() {
  canvas.width = 1300;
  canvas.height = 800;
  draw();
}

window.addEventListener("resize", resizeCanvas);

function gridToIso(x, y) {
  return {
    x: ((x - y) * TILE_W) / 2,
    y: ((x + y) * TILE_H) / 2
  };
}

function getIsoOffset() {
  return {
    x: canvas.width / 2,
    y: 10
  };
}

function drawTile(x, y) {
  const pos = gridToIso(x, y);
  const offset = getIsoOffset();

  const sx = pos.x + offset.x;
  const sy = pos.y + offset.y;

  ctx.beginPath();
  ctx.moveTo(sx, sy);
  ctx.lineTo(sx + TILE_W / 2, sy + TILE_H / 2);
  ctx.lineTo(sx, sy + TILE_H);
  ctx.lineTo(sx - TILE_W / 2, sy + TILE_H / 2);
  ctx.closePath();

  ctx.fillStyle = "#4caf50";
  ctx.fill();

  ctx.strokeStyle = "#2e7d32";
  ctx.stroke();
}

function drawGrid() {
  for (let y = 0; y < GRID_H; y++) {
    for (let x = 0; x < GRID_W; x++) {
      drawTile(x, y);
    }
  }
}

function drawCube(x, y, colors, height = 32) {
  const pos = gridToIso(x, y);
  const offset = getIsoOffset();

  const sx = pos.x + offset.x;
  const sy = pos.y + offset.y;
  const h = height;

  const top = { x: sx, y: sy };
  const right = { x: sx + TILE_W / 2, y: sy + TILE_H / 2 };
  const bottom = { x: sx, y: sy + TILE_H };
  const left = { x: sx - TILE_W / 2, y: sy + TILE_H / 2 };

  const top2 = { x: top.x, y: top.y - h };
  const right2 = { x: right.x, y: right.y - h };
  const bottom2 = { x: bottom.x, y: bottom.y - h };
  const left2 = { x: left.x, y: left.y - h };

  ctx.strokeStyle = "#333";

  ctx.beginPath();
  ctx.moveTo(left.x, left.y);
  ctx.lineTo(bottom.x, bottom.y);
  ctx.lineTo(bottom2.x, bottom2.y);
  ctx.lineTo(left2.x, left2.y);
  ctx.closePath();
  ctx.fillStyle = colors.left;
  ctx.fill();
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(right.x, right.y);
  ctx.lineTo(bottom.x, bottom.y);
  ctx.lineTo(bottom2.x, bottom2.y);
  ctx.lineTo(right2.x, right2.y);
  ctx.closePath();
  ctx.fillStyle = colors.right;
  ctx.fill();
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(top2.x, top2.y);
  ctx.lineTo(right2.x, right2.y);
  ctx.lineTo(bottom2.x, bottom2.y);
  ctx.lineTo(left2.x, left2.y);
  ctx.closePath();
  ctx.fillStyle = colors.top;
  ctx.fill();
  ctx.stroke();
}

// --- PALETTES ---

const FRUIT = {
  top: "#ff5252",
  left: "#c62828",
  right: "#e53935"
};

const HEAD = {
  top: "#7FDBFF",
  right: "#3A86FF",
  left: "#1D4ED8"
};

const BODY = {
  top: "#F472FF",
  right: "#C026D3",
  left: "#7E22CE"
};

// --- API FUNCTIONS ---

async function loadGameState() {
  const response = await fetch("/projects/snake/api/state");

  if (!response.ok) {
    console.error("Erreur chargement état du jeu");
    return;
  }

  const state = await response.json();

  fruit = state.fruit;
  snake = state.snake ?? [];
  currentDirection = state.direction ?? currentDirection;

  if (state.mode) {
    const radio = document.querySelector(`input[name="gameMode"][value="${state.mode}"]`);
    if (radio) radio.checked = true;
    document.querySelectorAll('input[name="gameMode"]').forEach(input => { input.disabled = true; });
  }
  updateSpeedLabel();
  applyState(state);
}

function drawObjects() {
  if (!fruit && !snake.length) return;

  const objects = [];

  if (fruit) {
    objects.push({
      x: fruit.x,
      y: fruit.y,
      colors: FRUIT,
      height: 32
    });
  }

  snake.forEach((part, index) => {
    objects.push({
      x: part.x,
      y: part.y,
      colors: index === 0 ? HEAD : BODY,
      height: 32
    });
  });

  objects.sort((a, b) => {
    const da = a.x + a.y;
    const db = b.x + b.y;

    if (da !== db) return da - db;
    return a.y - b.y;
  });

  objects.forEach(obj => {
    drawCube(obj.x, obj.y, obj.colors, obj.height);
  });
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawGrid();
  drawObjects();
}

async function moveSnake(direction) {
  const mode = getGameMode();

  const response = await fetch(`/projects/snake/api/move/${direction}/${mode}`, {
    method: "POST"
  });

  if (!response.ok) {
    throw new Error("Erreur déplacement");
  }

  const state = await response.json();
  applyState(state);
}

async function moveSnakeAI() {

  const response = await fetch(`/projects/snake/api/ai/move`, {
    method: "POST"
  });

  if (!response.ok) {
    throw new Error("Erreur de déplacement IA");
  }

  const state = await response.json();
  applyState(state);
}

async function moveSnakeAstarNN() {
  const response = await fetch(`/projects/snake/api/rl/move`, {
    method: "POST"
  });
  const state = await response.json();
  if (!response.ok) {
    stopGame();
    alert(state.error ?? "Erreur du réseau de neurones");
    return;
  }
  applyState(state);
}

function applyState(state) {
  fruit = state.fruit;
  snake = state.snake ?? [];
  currentDirection = state.direction ?? currentDirection;

  updateStats(state);
  draw();

  if (state.game_over) {
    stopGame();
    finishGame(state);
  }
}

// --- CONTROLS ---

const oppositeDirections = {
  up: "down",
  down: "up",
  left: "right",
  right: "left"
};

window.addEventListener("keydown", event => {
  const keyToDirection = {
    ArrowUp: "up",
    ArrowDown: "down",
    ArrowLeft: "left",
    ArrowRight: "right"
  };

  const newDirection = keyToDirection[event.key];

  if (!newDirection || getGameMode() !== "human") return;
  if (["INPUT", "TEXTAREA", "SELECT"].includes(event.target?.tagName)) return;
  event.preventDefault();

  if (oppositeDirections[currentDirection] !== newDirection) {
    currentDirection = newDirection;
  }
});

// --- GAME MANAGEMENT ---

function getGameMode() {
  return document.querySelector('input[name="gameMode"]:checked')?.value ?? "human";
}

function updateStats(state) {
  document.getElementById("score").textContent = state.score ?? 0;
  document.getElementById("stepsSinceFruit").textContent = state.steps_since_fruit ?? 0;
  document.getElementById("totalSteps").textContent = state.total_steps ?? 0;
}

function getMoveDelay() {
  const value = Number(document.getElementById("speedSlider").value);
  const fraction = (Math.max(1, Math.min(10, value)) - 1) / 9;
  // Human: 1,000 to 200 ms per move. AI: 500 to 40 ms.
  const [slow, fast] = getGameMode() === "human" ? [1000, 200] : [500, 40];
  return Math.round(slow - fraction * (slow - fast));
}

function updateSpeedLabel() {
  const human = getGameMode() === "human";
  document.getElementById("humanHints").hidden = !human;
  document.getElementById("recordControls").hidden = !human;
  document.getElementById("recordStats").disabled = !human || gameLoop !== null;
  const delay = getMoveDelay();
  document.getElementById("speedValue").textContent =
    `${(1000 / delay).toFixed(1)} cases/s (${delay} ms)`;
}

function scheduleMove(generation, delay = getMoveDelay()) {
  gameLoop = setTimeout(async () => {
    if (generation !== loopGeneration) return;
    isMoving = true;
    const started = performance.now();
    try {
      const mode = getGameMode();
      if (mode === "human") {
        movementPromise = moveSnake(currentDirection);
        await movementPromise;
      } else if (mode === "astar") {
        movementPromise = moveSnakeAI();
        await movementPromise;
      } else if (mode === "astar_nn") {
        movementPromise = moveSnakeAstarNN();
        await movementPromise;
      }
    } catch (error) {
      console.error(error);
      stopGame();
    } finally {
      isMoving = false;
      movementPromise = null;
      if (generation === loopGeneration && gameLoop !== null) {
        // No overlapping requests; respect the selected cadence including request time.
        scheduleMove(generation, Math.max(0, getMoveDelay() - (performance.now() - started)));
      }
    }
  }, delay);
}

function startGame() {
  if (gameLoop !== null || isMoving || isResetting || finishedGame) return;
  document.querySelectorAll('input[name="gameMode"]').forEach(input => { input.disabled = true; });
  document.getElementById("recordStats").disabled = true;
  scheduleMove(++loopGeneration);
}

function stopGame() {
  ++loopGeneration;
  clearTimeout(gameLoop);
  gameLoop = null;
}

function changeSpeed() {
  updateSpeedLabel();
  if (gameLoop !== null && !isMoving) {
    clearTimeout(gameLoop);
    scheduleMove(++loopGeneration);
  }
}

async function resetGame() {
  if (isResetting) return;
  isResetting = true;
  stopGame();
  if (movementPromise) await movementPromise.catch(() => {});
  finishedGame = null;
  document.getElementById("resultPanel").hidden = true;
  currentDirection = "right";

  try {
    const response = await fetch("/projects/snake/api/reset", {method: "POST"});
    if (!response.ok) throw new Error("Réinitialisation impossible");
    applyState(await response.json());
    document.querySelectorAll('input[name="gameMode"]').forEach(input => { input.disabled = false; });
    updateSpeedLabel();
  } catch (error) {
    document.getElementById("recordStatus").textContent = error.message;
    document.getElementById("resultPanel").hidden = false;
  } finally {
    isResetting = false;
  }
}

function isRecordingEnabled() {
  return getGameMode() === "human" && (document.getElementById("recordStats")?.checked ?? false);
}

async function saveFinishedGame(state) {
  const response = await fetch("/projects/snake/api/results", {
    method: "POST",
    headers: {"Content-Type": "application/json",
              "X-Admin-Token": document.getElementById("recordToken").value},
    body: JSON.stringify({game_id: state.game_id})
  });
  if (!response.ok) throw new Error(response.status === 403
    ? "Enregistrement refusé : renseigne le jeton administrateur puis réessaie."
    : "Enregistrement impossible. Tu peux réessayer.");
}

async function finishGame(state) {
  if (finishedGame?.game_id === state.game_id) return;
  finishedGame = state;
  document.getElementById("resultPanel").hidden = false;
  document.getElementById("gameSummary").textContent =
    `${state.message || "Partie terminée"} Score : ${state.score} · Cases parcourues : ${state.total_steps}.`;
  document.getElementById("retryRecord").hidden = true;
  if (isRecordingEnabled()) await recordFinishedGame();
  else document.getElementById("recordStatus").textContent = "Partie non enregistrée.";
  await loadResults();
}

async function recordFinishedGame() {
  const state = finishedGame;
  if (!state) return;
  const status = document.getElementById("recordStatus");
  const button = document.getElementById("retryRecord");
  button.disabled = true;
  try {
    await saveFinishedGame(state);
    if (finishedGame !== state) return;
    status.textContent = "Résultat enregistré.";
    button.hidden = true;
    await loadResults();
  } catch (error) {
    if (finishedGame !== state) return;
    status.textContent = error.message;
    button.hidden = false;
  } finally {
    button.disabled = false;
  }
}

async function loadResults() {
  if (statsLoading) return;
  statsLoading = true;
  const status = document.getElementById("statsStatus");
  const labels = {human: "Humain", astar: "IA (A*)", astar_nn: "IA + NN (DQN)"};
  const reasons = {collision: "Collision", no_path: "Aucun chemin", board_full: "Plateau rempli",
                   step_limit: "Limite de déplacements", no_progress: "Sans progression"};
  try {
    const response = await fetch("/projects/snake/api/results");
    if (!response.ok) throw new Error("Chargement impossible");
    const rows = await response.json();
    const body = document.getElementById("resultsBody");
    body.replaceChildren();
    rows.forEach(result => {
      const row = document.createElement("tr");
      [labels[result.mode] || result.mode, result.score, result.total_steps,
       reasons[result.end_reason] || result.end_reason].forEach(value => {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.appendChild(cell);
      });
      body.appendChild(row);
    });
    status.textContent = rows.length ? "Résultats des parties terminées (100 dernières)." : "Aucune partie enregistrée.";
  } catch (error) {
    status.textContent = "Impossible de charger les résultats.";
  } finally {
    statsLoading = false;
  }
}

document.getElementById("startGame").addEventListener("click", startGame);
document.getElementById("stopGame").addEventListener("click", stopGame);
document.getElementById("resetGame").addEventListener("click", resetGame);

document.getElementById("speedSlider").addEventListener("input", changeSpeed);
document.querySelectorAll('input[name="gameMode"]').forEach(input => {
  input.addEventListener("change", () => { updateSpeedLabel(); resetGame(); });
});
updateSpeedLabel();
resizeCanvas();
loadGameState();

document.getElementById("retryRecord").addEventListener("click", recordFinishedGame);
