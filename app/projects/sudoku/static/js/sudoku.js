const shuffleBtn = document.getElementById("shuffleBtn");
const solveBtn = document.getElementById("solveBtn");
const hideBtn = document.getElementById("hideBtn");
const animateBtn = document.getElementById("animateBtn");
const board = document.getElementById("sudoku-board");

let currentSolution = null;
let currentPuzzle = null;
let currentSolvedGrid = null;
let solutionVisible = false;
let animationRunning = false;

const speedSlider = document.getElementById("speedSlider");
const speedValue = document.getElementById("speedValue");
let animationSpeed = 80;

let stepMode = false;
let waitingResolver = null;
const stepModeToggle = document.getElementById("stepModeToggle");

let emptyCells = 30;
const difficultyRadios = document.querySelectorAll(
  'input[name="difficulty"]'
);

const BASE_GRID = [
  [5, 3, 4, 6, 7, 8, 9, 1, 2],
  [6, 7, 2, 1, 9, 5, 3, 4, 8],
  [1, 9, 8, 3, 4, 2, 5, 6, 7],
  [8, 5, 9, 7, 6, 1, 4, 2, 3],
  [4, 2, 6, 8, 5, 3, 7, 9, 1],
  [7, 1, 3, 9, 2, 4, 8, 5, 6],
  [9, 6, 1, 5, 3, 7, 2, 8, 4],
  [2, 8, 7, 4, 1, 9, 6, 3, 5],
  [3, 4, 5, 2, 8, 6, 1, 7, 9],
];

function deepCopyGrid(grid) {
  return grid.map(row => [...row]);
}

function randomInt(max) {
  return Math.floor(Math.random() * max);
}

function swapRows(grid, r1, r2) {
  [grid[r1], grid[r2]] = [grid[r2], grid[r1]];
}

function swapCols(grid, c1, c2) {
  for (let i = 0; i < 9; i++) {
    [grid[i][c1], grid[i][c2]] = [grid[i][c2], grid[i][c1]];
  }
}

function swapNumbers(grid, n1, n2) {
  for (let i = 0; i < 9; i++) {
    for (let j = 0; j < 9; j++) {
      if (grid[i][j] === n1) grid[i][j] = n2;
      else if (grid[i][j] === n2) grid[i][j] = n1;
    }
  }
}

function shuffleSudoku() {
  const grid = deepCopyGrid(BASE_GRID);

  for (let k = 0; k < 20; k++) {
    const action = randomInt(3);

    if (action === 0) {
      const band = randomInt(3) * 3;
      swapRows(grid, band + randomInt(3), band + randomInt(3));
    } else if (action === 1) {
      const stack = randomInt(3) * 3;
      swapCols(grid, stack + randomInt(3), stack + randomInt(3));
    } else {
      let n1 = 1 + randomInt(9);
      let n2 = 1 + randomInt(9);

      while (n1 === n2) {
        n2 = 1 + randomInt(9);
      }

      swapNumbers(grid, n1, n2);
    }
  }

  return grid;
}

function createPuzzleFromSolution(solution, emptyCells = 40) {
  const puzzle = deepCopyGrid(solution);
  let removed = 0;

  while (removed < emptyCells) {
    const row = randomInt(9);
    const col = randomInt(9);

    if (puzzle[row][col] !== 0) {
      puzzle[row][col] = 0;
      removed++;
    }
  }

  return puzzle;
}

function getCellClasses(i, j, value, originalGrid) {
  let classes =
    "w-8 h-8 sm:w-12 sm:h-12 flex items-center justify-center text-sm sm:text-lg font-bold border border-gray-400";

  if ((j + 1) % 3 === 0 && j < 8) {
    classes += " border-r-4 border-r-black";
  }

  if ((i + 1) % 3 === 0 && i < 8) {
    classes += " border-b-4 border-b-black";
  }

  if (value === 0) {
    classes += " text-gray-400 bg-white";
  } else if (originalGrid && originalGrid[i][j] !== 0) {
    classes += " text-black bg-gray-100";
  } else {
    classes += " text-blue-600 bg-blue-50";
  }

  return classes;
}

function renderGrid(grid, originalGrid = currentPuzzle) {
  board.innerHTML = "";

  for (let i = 0; i < 9; i++) {
    for (let j = 0; j < 9; j++) {
      const cell = document.createElement("div");
      const value = grid[i][j];

      cell.className = getCellClasses(i, j, value, originalGrid);
      cell.textContent = value === 0 ? "" : value;

      board.appendChild(cell);
    }
  }
}

function getPossibleNumbers(grid, row, col) {
  if (grid[row][col] !== 0) return [];

  const used = new Set();

  for (let i = 0; i < 9; i++) {
    used.add(grid[row][i]);
    used.add(grid[i][col]);
  }

  const boxRow = Math.floor(row / 3) * 3;
  const boxCol = Math.floor(col / 3) * 3;

  for (let i = boxRow; i < boxRow + 3; i++) {
    for (let j = boxCol; j < boxCol + 3; j++) {
      used.add(grid[i][j]);
    }
  }

  const possibilities = [];

  for (let n = 1; n <= 9; n++) {
    if (!used.has(n)) {
      possibilities.push(n);
    }
  }

  return possibilities;
}

function getCellToExplore(grid) {
  let bestCell = null;
  let bestPossibilities = null;

  for (let row = 0; row < 9; row++) {
    for (let col = 0; col < 9; col++) {
      if (grid[row][col] === 0) {
        const possibilities = getPossibleNumbers(grid, row, col);

        if (possibilities.length === 0) {
          return { row, col, possibilities: [] };
        }

        if (
          bestCell === null ||
          possibilities.length < bestPossibilities.length
        ) {
          bestCell = { row, col };
          bestPossibilities = possibilities;
        }
      }
    }
  }

  if (bestCell === null) return null;

  return {
    row: bestCell.row,
    col: bestCell.col,
    possibilities: bestPossibilities,
  };
}

function solveBestFirst(grid) {
  const cell = getCellToExplore(grid);

  if (cell === null) return true;
  if (cell.possibilities.length === 0) return false;

  const { row, col, possibilities } = cell;

  for (const number of possibilities) {
    grid[row][col] = number;

    if (solveBestFirst(grid)) {
      return true;
    }

    grid[row][col] = 0;
  }

  return false;
}

function solveCurrentPuzzle() {
  if (!currentPuzzle || animationRunning) return;

  const gridCopy = deepCopyGrid(currentPuzzle);

  if (solveBestFirst(gridCopy)) {
    currentSolvedGrid = gridCopy;
    renderGrid(currentSolvedGrid, currentPuzzle);
    solutionVisible = true;
  } else {
    console.log("Aucune solution trouvée");
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function renderGridWithActiveCell(
  grid,
  originalGrid,
  activeCell = null,
  mode = "try"
) {
  board.innerHTML = "";

  for (let i = 0; i < 9; i++) {
    for (let j = 0; j < 9; j++) {
      const cell = document.createElement("div");
      const value = grid[i][j];

      let classes = getCellClasses(i, j, value, originalGrid);

      if (activeCell && activeCell.row === i && activeCell.col === j) {
        classes +=
          mode === "backtrack"
            ? " text-red-600 bg-red-100"
            : " text-purple-700 bg-purple-100";
      }

      cell.className = classes;
      cell.textContent = value === 0 ? "" : value;

      board.appendChild(cell);
    }
  }
}

async function solveBestFirstAnimated(grid, delay = 80) {
  const cell = getCellToExplore(grid);

  if (cell === null) return true;
  if (cell.possibilities.length === 0) return false;

  const { row, col, possibilities } = cell;

  for (const number of possibilities) {
    grid[row][col] = number;

    renderGridWithActiveCell(grid, currentPuzzle, { row, col }, "try");
    if (stepMode) {
      await waitForNextStep();
    } else {
      await sleep(delay);
    }

    if (await solveBestFirstAnimated(grid, delay)) {
      return true;
    }

    grid[row][col] = 0;

    renderGridWithActiveCell(grid, currentPuzzle, { row, col }, "backtrack");
    await sleep(delay);
  }

  return false;
}

async function animateCurrentPuzzle() {
  if (!currentPuzzle || animationRunning) return;

  animationRunning = true;
  solutionVisible = false;

  const gridCopy = deepCopyGrid(currentPuzzle);
  const solved = await solveBestFirstAnimated(gridCopy, animationSpeed);

  if (solved) {
    currentSolvedGrid = gridCopy;
    renderGrid(currentSolvedGrid, currentPuzzle);
    solutionVisible = true;
  } else {
    renderGrid(currentPuzzle, currentPuzzle);
    console.log("Aucune solution trouvée");
  }

  animationRunning = false;
}

async function waitForNextStep() {
  return new Promise(resolve => {
    waitingResolver = resolve;
  });
}

// --- Event Listeners ---

shuffleBtn.addEventListener("click", () => {
  if (animationRunning) return;

  currentSolution = shuffleSudoku();
  currentPuzzle = createPuzzleFromSolution(
    currentSolution,
    emptyCells
  );
  currentSolvedGrid = null;
  solutionVisible = false;

  renderGrid(currentPuzzle, currentPuzzle);
});

solveBtn.addEventListener("click", () => {
  solveCurrentPuzzle();
});

hideBtn.addEventListener("click", () => {
  if (!currentPuzzle || animationRunning) return;

  renderGrid(currentPuzzle, currentPuzzle);
  solutionVisible = false;
});

animateBtn.addEventListener("click", () => {
  animateCurrentPuzzle();
});

speedSlider.addEventListener("input", (e) => {
  animationSpeed = Number(e.target.value);
  speedValue.textContent = `${animationSpeed} ms`;
});

stepBtn.addEventListener("click", () => {
  if (waitingResolver) {
    waitingResolver();
  }
});

stepModeToggle.addEventListener("change", (e) => {
  stepMode = e.target.checked;
});

difficultyRadios.forEach(radio => {
  radio.addEventListener("change", (e) => {
    emptyCells = Number(e.target.value);

    console.log("Difficulté :", emptyCells);
  });
});