const controls = document.getElementById("controls");
let currentPlayer = 1;
let isAITurnRunning = false;
let gameOver = false;

const BASE_GRID = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0]
];

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function switchPlayer() {
    currentPlayer = currentPlayer === 1 ? 2 : 1;
}

function renderGrid(grid) {
    const container = document.getElementById("connectFour-board");
    container.innerHTML = "";

    for (let i = 0; i < 6; i++) {
        const row = document.createElement("div");
        row.classList.add("flex");

        for (let j = 0; j < 7; j++) {
            const cell = document.createElement("div");
            cell.classList.add(
                "w-8", "h-8", "sm:w-12", "sm:h-12",
                "border", "border-gray-400", "rounded-full",
                "mx-2", "my-2"
            );

            if (grid[i][j] === 1) cell.classList.add("bg-red-500");
            else if (grid[i][j] === 2) cell.classList.add("bg-yellow-300");
            else cell.classList.add("bg-white");

            row.appendChild(cell);
        }

        container.appendChild(row);
    }
}

function countPieces(grid) {
    const count = { 1: 21, 2: 21 };

    for (const row of grid) {
        for (const cell of row) {
            if (cell === 1 || cell === 2) count[cell]--;
        }
    }

    return count;
}

function showPiecesCount() {
    const count = countPieces(BASE_GRID);
    const player1 = document.getElementById("player1-count");
    const player2 = document.getElementById("player2-count");

    player1.textContent = `Player 1: ${count[1]}`;
    player2.textContent = `Player 2: ${count[2]}`;

    player1.classList.toggle("font-bold", currentPlayer === 1);
    player2.classList.toggle("font-bold", currentPlayer === 2);
}

function playMove(grid, column, player) {
    for (let i = 5; i >= 0; i--) {
        if (grid[i][column] === 0) {
            grid[i][column] = player;
            return true;
        }
    }
    return false;
}

function checkWin(grid, player) {
    for (let i = 0; i < 6; i++) {
        for (let j = 0; j < 7; j++) {
            if (
                (j <= 3 && grid[i][j] === player && grid[i][j + 1] === player && grid[i][j + 2] === player && grid[i][j + 3] === player) ||
                (i <= 2 && grid[i][j] === player && grid[i + 1][j] === player && grid[i + 2][j] === player && grid[i + 3][j] === player) ||
                (i <= 2 && j <= 3 && grid[i][j] === player && grid[i + 1][j + 1] === player && grid[i + 2][j + 2] === player && grid[i + 3][j + 3] === player) ||
                (i >= 3 && j <= 3 && grid[i][j] === player && grid[i - 1][j + 1] === player && grid[i - 2][j + 2] === player && grid[i - 3][j + 3] === player)
            ) {
                return true;
            }
        }
    }
    return false;
}

function isGridFull(grid) {
    return grid[0].every(cell => cell !== 0);
}

function getPlayerTypes() {
    return {
        1: document.getElementById("human1").checked ? "human" : "ai",
        2: document.getElementById("human2").checked ? "human" : "ai"
    };
}

function getAIType() {
    return document.querySelector('input[name="aiType"]:checked').value;
}

async function getAIMove(grid, player, type = "easy") {
    const response = await fetch("/projects/connect_four/api/ai-move", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ grid, player, type })
    });

    const data = await response.json();
    return data.column;
}

function endGame(message) {
    gameOver = true;
    renderGrid(BASE_GRID);
    showPiecesCount();
    alert(message);
}

async function playTurn(column) {
    if (gameOver) return false;

    if (!playMove(BASE_GRID, column, currentPlayer)) {
        alert("Column is full!");
        return false;
    }

    renderGrid(BASE_GRID);

    if (checkWin(BASE_GRID, currentPlayer)) {
        endGame(`Player ${currentPlayer} wins!`);
        return false;
    }

    if (isGridFull(BASE_GRID)) {
        endGame("Draw!");
        return false;
    }

    switchPlayer();
    showPiecesCount();

    return true;
}

// Fonction pour gérer les tours de l'IA de manière asynchrone 
// et éviter les conflits avec les actions humaines
async function playAITurnsIfNeeded() {
    if (isAITurnRunning || gameOver) return;

    isAITurnRunning = true;

    while (!gameOver && getPlayerTypes()[currentPlayer] === "ai") {
        await sleep(700);

        const aiColumn = await getAIMove(
            BASE_GRID,
            currentPlayer,
            getAIType()
        );

        if (aiColumn === null || aiColumn === undefined) {
            endGame("No available moves.");
            break;
        }

        await playTurn(aiColumn);
    }

    isAITurnRunning = false;
}

// Création des boutons de contrôle pour chaque colonne
for (let column = 0; column < 7; column++) {
    const button = document.createElement("button");
    button.textContent = "▼";
    button.dataset.column = column;

    button.classList.add(
        "column-button",
        "w-8", "h-8", "sm:w-12", "sm:h-12",
        "hover:bg-gray-200",
        "border", "border-gray-400", "rounded-full",
        "mx-2", "my-2"
    );

    button.addEventListener("click", async () => {
        if (gameOver) return;
        if (isAITurnRunning) return;
        if (getPlayerTypes()[currentPlayer] === "ai") return;

        const success = await playTurn(column);

        if (success) {
            await playAITurnsIfNeeded();
        }
    });

    controls.appendChild(button);
}

function resetGame() {
    for (let i = 0; i < 6; i++) {
        for (let j = 0; j < 7; j++) {
            BASE_GRID[i][j] = 0;
        }
    }

    currentPlayer = 1;
    gameOver = false;
    isAITurnRunning = false;

    renderGrid(BASE_GRID);
    showPiecesCount();
    playAITurnsIfNeeded();
}

document.getElementById("resetGame").addEventListener("click", resetGame);

// Initialisation du jeu
renderGrid(BASE_GRID);
showPiecesCount();
playAITurnsIfNeeded();