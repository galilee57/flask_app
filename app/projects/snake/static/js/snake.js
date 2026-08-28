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

  updateStats(state);
  draw();
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
  const record = isRecordingEnabled();

  const response = await fetch(`/projects/snake/api/move/${direction}/${mode}?record=${record}`, {
    method: "POST"
  });

  if (!response.ok) {
    console.error("Erreur déplacement");
    return;
  }

  const state = await response.json();
  applyState(state);
}

async function moveSnakeAI() {
  const record = isRecordingEnabled();

  const response = await fetch(`/projects/snake/api/ai/move?record=${record}`, {
    method: "POST"
  });

  if (!response.ok) {
    console.error("Erreur de déplacement IA");
    return;
  }

  const state = await response.json();
  applyState(state);
}

async function moveSnakeAstarNN() {
  return moveSnakeAI();
}

function applyState(state) {
  fruit = state.fruit;
  snake = state.snake ?? [];
  currentDirection = state.direction ?? currentDirection;

  updateStats(state);
  draw();

  if (state.game_over) {
    stopGame();
    alert(state.message ?? "GAME OVER");
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

  if (!newDirection) return;

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

function startGame() {
  if (gameLoop !== null) return;

  const time = Number(document.querySelector("#speedSlider").value);

  gameLoop = setInterval(async () => {
    if (isMoving) return;

    isMoving = true;

    try {
      const mode = getGameMode();

      if (mode === "human") {
        await moveSnake(currentDirection);
      } else if (mode === "astar") {
        await moveSnakeAI();
      } else if (mode === "astar_nn") {
        await moveSnakeAstarNN();
      }
    } finally {
      isMoving = false;
    }
  }, time);
}

function stopGame() {
  if (gameLoop === null) return;

  clearInterval(gameLoop);
  gameLoop = null;
}

async function resetGame() {
  stopGame();

  currentDirection = "right";

  const response = await fetch("/projects/snake/api/reset", {
    method: "POST"
  });

  if (!response.ok) {
    console.error("Erreur reset");
    return;
  }

  const state = await response.json();
  applyState(state);
}

function isRecordingEnabled() {
  return document.getElementById("recordStats")?.checked ?? false;
}

async function loadStatsCurve() {
    const response = await fetch("/projects/snake/api/stats/curve");
    const data = await response.json();

    const modes = ["human", "astar", "astar_nn"];

    const datasets = modes.map(mode => {
        const modeData = data.filter(item => item.mode === mode);

        return {
            label: mode,
            data: modeData.map(item => ({
                x: item.score,
                y: item.avg_steps
            })),
            showLine: true,
            tension: 0.2
        };
    });

    const ctx = document.getElementById("statsChart");

    new Chart(ctx, {
        type: "scatter",
        data: {
            datasets: datasets
        },
        options: {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Score"
                    },
                    ticks: {
                        stepSize: 1
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: "Nombre moyen de cases parcourues"
                    }
                }
            }
        }
    });
}

loadStatsCurve();

document.getElementById("startGame").addEventListener("click", startGame);
document.getElementById("stopGame").addEventListener("click", stopGame);
document.getElementById("resetGame").addEventListener("click", resetGame);

resizeCanvas();
loadGameState();
loadStatsCurve();