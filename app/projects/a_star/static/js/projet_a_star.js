let state = [1, 2, 3, 4, 5, 6, 7, 8, 0];
let isAnimating = false;

const board = document.getElementById("board");
const message = document.getElementById("message");
const shuffleBtn = document.getElementById("shuffleBtn");
const solveBtn = document.getElementById("solveBtn");
const treeContainer = document.getElementById("tree");
const showTreeBtn = document.getElementById("showTreeBtn");

function renderBoard() {
    if (!board) return;

    board.innerHTML = "";

    state.forEach((value, index) => {
        const tile = document.createElement("div");

        tile.className =
            "flex h-[100px] w-[100px] items-center justify-center rounded-lg text-3xl font-bold select-none transition";

        if (value === 0) {
            tile.classList.add(
                "border-2",
                "border-dashed",
                "border-slate-300",
                "bg-white"
            );
            tile.textContent = "";
        } else {
            tile.classList.add(
                "cursor-pointer",
                "border",
                "border-slate-300",
                "bg-slate-50",
                "text-slate-800",
                "shadow-sm",
                "hover:bg-slate-100"
            );
            tile.textContent = value;

            if (!isAnimating) {
                tile.addEventListener("click", () => moveTile(index));
            }
        }

        board.appendChild(tile);
    });
}

function moveTile(tileIndex) {
    if (isAnimating) return;

    const emptyIndex = state.indexOf(0);
    const validMoves = getValidMoves(emptyIndex);

    if (validMoves.includes(tileIndex)) {
        [state[tileIndex], state[emptyIndex]] = [state[emptyIndex], state[tileIndex]];
        if (message) message.textContent = "";
        clearTree();
        renderBoard();
    }
}

function getValidMoves(emptyIndex) {
    const moves = [];
    const row = Math.floor(emptyIndex / 3);
    const col = emptyIndex % 3;

    if (row > 0) moves.push(emptyIndex - 3);
    if (row < 2) moves.push(emptyIndex + 3);
    if (col > 0) moves.push(emptyIndex - 1);
    if (col < 2) moves.push(emptyIndex + 1);

    return moves;
}

function shuffleBoard() {
    if (isAnimating) return;

    const values = [0, 1, 2, 3, 4, 5, 6, 7, 8];

    for (let i = values.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [values[i], values[j]] = [values[j], values[i]];
    }

    state = values;

    if (message) {
        message.textContent = isSolvable(state)
            ? "Taquin aléatoire résoluble."
            : "Taquin aléatoire non résoluble.";
    }

    clearTree();
    renderBoard();
}

function isSolvable(state) {
    const values = state.filter(value => value !== 0);
    let inversions = 0;

    for (let i = 0; i < values.length; i++) {
        for (let j = i + 1; j < values.length; j++) {
            if (values[i] > values[j]) {
                inversions++;
            }
        }
    }

    return inversions % 2 === 0;
}

async function solvePuzzle() {
    if (isAnimating) return;

    if (typeof SOLVE_URL === "undefined") {
        console.error("SOLVE_URL n'est pas défini.");
        if (message) message.textContent = "Erreur de configuration de l'URL Flask.";
        return;
    }

    try {
        if (message) message.textContent = "Résolution en cours...";

        const response = await fetch(SOLVE_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ state })
        });

        if (!response.ok) {
            throw new Error(`Erreur HTTP ${response.status}`);
        }

        const data = await response.json();

        if (!data.solvable) {
            if (message) message.textContent = "Ce taquin n'est pas résoluble.";
            clearTree();
            return;
        }

        if (message) {
            message.textContent = `Solution trouvée en ${data.moves} coups.`;
        }

        renderTree(data.tree_nodes || []);
        animateSolution(data.solution || []);
    } catch (error) {
        console.error(error);
        if (message) message.textContent = "Erreur lors de la résolution.";
    }
}

function animateSolution(solution) {
    if (!Array.isArray(solution) || solution.length === 0) {
        isAnimating = false;
        if (shuffleBtn) shuffleBtn.disabled = false;
        if (solveBtn) solveBtn.disabled = false;
        return;
    }

    isAnimating = true;
    if (shuffleBtn) shuffleBtn.disabled = true;
    if (solveBtn) solveBtn.disabled = true;

    let i = 0;

    const interval = setInterval(() => {
        state = [...solution[i]];
        renderBoard();
        i++;

        if (i >= solution.length) {
            clearInterval(interval);
            isAnimating = false;

            if (shuffleBtn) shuffleBtn.disabled = false;
            if (solveBtn) solveBtn.disabled = false;

            console.log("animation terminée, isAnimating =", isAnimating);
        }
    }, 500);
}

function formatState(state) {
    const display = state.map(value => (value === 0 ? " " : value));
    return `${display[0]} ${display[1]} ${display[2]}
${display[3]} ${display[4]} ${display[5]}
${display[6]} ${display[7]} ${display[8]}`;
}

function clearTree() {
    if (treeContainer) {
        treeContainer.innerHTML = "";
    }
}

function renderMiniBoard(state) {
    const container = document.createElement("div");

    container.className =
        "grid grid-cols-3 gap-[2px] bg-slate-200 p-[2px] rounded w-fit mx-auto";

    state.forEach(value => {
        const cell = document.createElement("div");

        cell.className =
            "w-6 h-6 flex items-center justify-center text-xs font-mono bg-white border border-slate-300 rounded";

        if (value === 0) {
            cell.classList.add("bg-slate-100", "text-transparent", "text-white");
            cell.textContent = "0"; // garde pour alignement
        } else {
            cell.textContent = value;
        }

        container.appendChild(cell);
    });

    return container.outerHTML;
}

function createNodeCard(node) {
    const card = document.createElement("div");

    let color = "bg-white";
    if (node.status === "goal") {
        color = "bg-green-100 border-green-400";
    } else if (node.status === "expanded") {
        color = "bg-blue-50";
    }

    card.className = `rounded-xl border p-3 shadow-sm ${color} w-fit shrink-0`;

    card.innerHTML = `
    <div class="text-sm font-semibold text-slate-700">Nœud ${node.id}</div>
    <div class="mb-2 text-xs text-slate-500">g=${node.g} | h=${node.h} | f=${node.f}</div>
    <pre class="rounded bg-slate-50 p-2 text-center text-sm leading-6 font-mono">${renderMiniBoard(node.state)}</pre>
    `;

    return card;
}

function renderTree(nodes) {
    if (!treeContainer) return;

    treeContainer.innerHTML = "";

    if (!Array.isArray(nodes) || nodes.length === 0) {
        treeContainer.innerHTML = "<p>Aucune trace disponible.</p>";
        return;
    }

    const levels = {};

    // Regrouper les nœuds par g
    nodes.forEach(node => {
        const g = node.g;

        if (!levels[g]) {
            levels[g] = [];
        }

        levels[g].push(node);
    });

    const sortedLevels = Object.keys(levels)
        .map(Number)
        .sort((a, b) => a - b);

    sortedLevels.forEach(level => {

        const row = document.createElement("div");
        row.className = "mb-6";

        const title = document.createElement("div");
        title.className = "mb-2 font-bold text-slate-600";
        title.textContent = `Profondeur g = ${level}`;

        const grid = document.createElement("div");
        grid.className = "flex flex-wrap gap-4";

        levels[level].forEach(node => {
            grid.appendChild(createNodeCard(node));
        });

        row.appendChild(title);
        row.appendChild(grid);

        treeContainer.appendChild(row);
    });
}

function renderNode(node, childrenMap, depth) {
    const wrapper = document.createElement("div");
    wrapper.className = "ml-0";

    const card = document.createElement("div");
    card.className = `rounded-xl border p-3 shadow-sm ${color} w-fit min-w-[120px]`;

    card.innerHTML = `
        <div class="font-semibold">Nœud ${node.id}</div>
        <div class="text-xs text-slate-600">g=${node.g}, h=${node.h}, f=${node.f}</div>
        <pre class="mt-2 rounded bg-white p-2 text-xs leading-5">${formatState(node.state)}</pre>
    `;

    wrapper.appendChild(card);

    const children = childrenMap[node.id] || [];
    children.forEach(child => {
        wrapper.appendChild(renderNode(child, childrenMap, depth + 1));
    });

    return wrapper;
}

function showTree() {
    const isHidden = treeContainer.classList.contains("hidden");

    if (isHidden) {
        treeContainer.classList.remove("hidden");
        treeContainer.classList.add("flex", "flex-col");
        showTreeBtn.textContent = "Masquer l'arbre de recherche";
    } else {
        treeContainer.classList.add("hidden");
        treeContainer.classList.remove("flex");
        showTreeBtn.textContent = "Afficher l'arbre de recherche";
    }
}

if (shuffleBtn) shuffleBtn.addEventListener("click", shuffleBoard);
if (solveBtn) solveBtn.addEventListener("click", solvePuzzle);
if (showTreeBtn) showTreeBtn.addEventListener("click", showTree);

renderBoard();