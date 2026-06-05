const controls = document.getElementById("controls");
let currentPlayer = 1;

const BASE_GRID = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0]
];

function renderGrid(grid) {
    const container = document.getElementById("connectFour-board");
    container.innerHTML = "";

    for (let i = 0; i < 6; i++) {
        const row = document.createElement("div");
        row.classList.add("flex");

        for (let j = 0; j < 7; j++) {
            const cell = document.createElement("div");
            cell.classList.add("w-8", "h-8", "sm:w-12", "sm:h-12", "border", "border-gray-400", "rounded-full", "mx-2", "my-2");

            if (grid[i][j] === 1) {
                cell.classList.add("bg-red-500");
            } else if (grid[i][j] === 2) {
                cell.classList.add("bg-yellow-300");
            } else {
                cell.classList.add("bg-white");
            }

            row.appendChild(cell);
        }

        container.appendChild(row);
    }
}

function countPieces(grid) {
    let count = { 1: 21, 2: 21 };

    for (const row of grid) {
        for (const cell of row) {
            if (cell === 1 || cell === 2) {
                count[cell]--;
            }
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

    player1.classList.remove("font-bold");
    player2.classList.remove("font-bold");

    // Le joueur en attente de jouer est affiché en gras
    if (currentPlayer === 1) {
        player1.classList.add("font-bold");
    } else {
        player2.classList.add("font-bold");
    }
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
    // Check horizontal, vertical, and diagonal for a win
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

// Get player types from the checkboxes
function getPlayerTypes() {
    return {
        1: document.getElementById("human1").checked ? "human" : "ai",
        2: document.getElementById("human2").checked ? "human" : "ai"
    };
}

// Request Flask backend to calculate AI move (not implemented yet)
async function getAIMove(grid, player, type = "easy") {
    const response = await fetch("/projects/connect_four/api/ai-move", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            grid: grid,
            player: player,
            type: type
        })
    });

    const data = await response.json();
    return data.column;

    console.log("Calling AI...", {
        grid,
        player,
        type
    });
}

// Create column buttons and add event listeners
for (let column = 0; column < 7; column++) {
    const button = document.createElement("button");
    button.textContent = "▼";
    button.dataset.column = column;
    button.classList.add("column-button", "w-8", "h-8", "sm:w-12", "sm:h-12", "border", "border-gray-400", "rounded-full", "mx-2", "my-2");
    
    button.addEventListener("click", () => {
        /// Coup du joueur courant
        if (!playMove(BASE_GRID, column, currentPlayer)) {
            alert("Column is full!");
            return;
        }
        renderGrid(BASE_GRID);

        if (checkWin(BASE_GRID, currentPlayer)) {
            alert(`Player ${currentPlayer} wins!`);
            return;
        }

        // Changement de joueur
        currentPlayer = currentPlayer === 1 ? 2 : 1;
        showPiecesCount();

        // Before asking the next player to play, check if it's an AI or a human
        playerTypes = getPlayerTypes();
        
        // Si le prochain joueur est une IA, demander son coup
        if (playerTypes[currentPlayer] === "ai") {
            getAIMove(BASE_GRID, currentPlayer).then(aiColumn => {
                if (!playMove(BASE_GRID, aiColumn, currentPlayer)) {
                    alert("AI chose a full column!");
                    return;
                }
                renderGrid(BASE_GRID);

                if (checkWin(BASE_GRID, currentPlayer)) {
                    alert(`Player ${currentPlayer} wins!`);
                    return;
                }

                // Changement de joueur
                currentPlayer = currentPlayer === 1 ? 2 : 1;
                showPiecesCount();
            });
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
    renderGrid(BASE_GRID);
    showPiecesCount();
}

// Add event listener to reset button
document.getElementById("resetGame").addEventListener("click", resetGame);

// Initial render
renderGrid(BASE_GRID);
showPiecesCount();