/* Pure game engine, shared by the browser and Node regression tests. */
(function (root) {
    const SHAPES = {
        I: [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
        J: [[1,0,0],[1,1,1],[0,0,0]], L: [[0,0,1],[1,1,1],[0,0,0]],
        O: [[1,1],[1,1]], S: [[0,1,1],[1,1,0],[0,0,0]],
        T: [[0,1,0],[1,1,1],[0,0,0]], Z: [[1,1,0],[0,1,1],[0,0,0]],
    };
    const rotate = matrix => matrix[0].map((_, x) => matrix.map(row => row[x]).reverse());
    class Game {
        constructor(random = Math.random) {
            this.random = random;
            this.board = Array.from({length: 20}, () => Array(10).fill(null));
            this.bag = []; this.score = 0; this.lines = 0; this.over = false;
            this.next = this.draw(); this.spawn();
        }
        draw() {
            if (!this.bag.length) {
                this.bag = Object.keys(SHAPES);
                for (let i = this.bag.length - 1; i > 0; i--) {
                    const j = Math.floor(this.random() * (i + 1));
                    [this.bag[i], this.bag[j]] = [this.bag[j], this.bag[i]];
                }
            }
            return this.bag.pop();
        }
        spawn() {
            const type = this.next;
            this.next = this.draw();
            this.piece = {type, matrix: SHAPES[type].map(row => [...row]), x: Math.floor((10 - SHAPES[type].length) / 2), y: 0};
            if (!this.valid(this.piece)) this.over = true;
        }
        valid(piece) {
            return piece.matrix.every((row, y) => row.every((cell, x) => !cell || (
                piece.x + x >= 0 && piece.x + x < 10 && piece.y + y >= 0 && piece.y + y < 20 &&
                !this.board[piece.y + y][piece.x + x]
            )));
        }
        move(dx, dy) {
            if (this.over) return false;
            const moved = {...this.piece, x: this.piece.x + dx, y: this.piece.y + dy};
            if (!this.valid(moved)) return false;
            this.piece = moved; return true;
        }
        turn() {
            if (this.over) return false;
            const matrix = rotate(this.piece.matrix);
            for (const dx of [0, -1, 1, -2, 2]) {
                const moved = {...this.piece, matrix, x: this.piece.x + dx};
                if (this.valid(moved)) { this.piece = moved; return true; }
            }
            return false;
        }
        lock() {
            if (this.over) return;
            this.piece.matrix.forEach((row, y) => row.forEach((cell, x) => {
                if (cell) this.board[this.piece.y + y][this.piece.x + x] = this.piece.type;
            }));
            const remaining = this.board.filter(row => !row.every(Boolean));
            const cleared = 20 - remaining.length;
            this.score += [0, 100, 300, 500, 800][cleared];
            this.lines += cleared;
            this.board = [...Array.from({length: cleared}, () => Array(10).fill(null)), ...remaining];
            this.spawn();
        }
        action(action) {
            if (this.over) return;
            if (action === 'left') this.move(-1, 0);
            else if (action === 'right') this.move(1, 0);
            else if (action === 'rotate') this.turn();
            else if (action === 'down') { if (this.move(0, 1)) this.score++; else this.lock(); }
            else if (action === 'drop') { while (this.move(0, 1)) this.score += 2; this.lock(); }
        }
        tick() { if (!this.over && !this.move(0, 1)) this.lock(); }
        snapshot() {
            return JSON.parse(JSON.stringify({board: this.board, piece: this.piece, next: this.next, score: this.score, lines: this.lines, over: this.over}));
        }
    }
    // Temporary agent. Evaluate placements reachable by rotation and translation before dropping.
    function analyze(state) {
        const candidates = [], seen = new Set();
        for (let turns = 0; turns < 4; turns++) {
            for (let shift = -9; shift <= 9; shift++) {
                const sim = new Game(() => 0.5);
                sim.board = state.board.map(row => [...row]);
                sim.piece = JSON.parse(JSON.stringify(state.piece)); sim.over = false; sim.next = state.next;
                const actions = [];
                let reachable = true;
                for (let r = 0; r < turns; r++) { if (!sim.turn()) reachable = false; actions.push('rotate'); }
                for (let s = 0; s < Math.abs(shift); s++) {
                    if (!sim.move(Math.sign(shift), 0)) reachable = false;
                    actions.push(shift < 0 ? 'left' : 'right');
                }
                if (!reachable) continue;
                while (sim.move(0, 1)) {} // Evaluate the exact landing before line removal.
                const landing = JSON.parse(JSON.stringify(sim.piece));
                const cells = [];
                landing.matrix.forEach((row, y) => row.forEach((v, x) => { if (v) cells.push(`${landing.x + x},${landing.y + y}`); }));
                const key = cells.sort().join(';');
                if (seen.has(key)) continue;
                seen.add(key);
                sim.lock();
                const heights = Array.from({length: 10}, (_, x) => {
                    const top = sim.board.findIndex(row => row[x]); return top < 0 ? 0 : 20 - top;
                });
                let holes = 0;
                heights.forEach((h, x) => { for (let y = 20 - h; y < 20; y++) if (!sim.board[y][x]) holes++; });
                const roughness = heights.slice(1).reduce((sum, h, i) => sum + Math.abs(h - heights[i]), 0);
                const value = sim.lines * 8 - heights.reduce((a,b) => a+b, 0) * 0.5 - holes * 7 - roughness * 0.3 - (sim.over ? 10000 : 0);
                candidates.push({actions: [...actions, 'drop'], landing, value, lines: sim.lines, height: heights.reduce((a,b) => a+b, 0), holes, roughness, over: sim.over, turns, column: Math.min(...cells.map(c => Number(c.split(',')[0]))) + 1});
            }
        }
        candidates.sort((a, b) => b.value - a.value);
        return {candidates, best: candidates[0]};
    }
    function heuristic(state) { return analyze(state).best?.actions || ['drop']; }
    // One visible operation per step. No gravity runs alongside the AI plan.
    class AIPlayback {
        constructor(game, actions) {
            if (!Array.isArray(actions) || actions.length > 40 || actions.some(a => !['left','right','rotate','drop'].includes(a))) throw new Error('Actions invalides');
            this.game = game;
            const end = actions.indexOf('drop');
            this.actions = actions.slice(0, end < 0 ? actions.length : end);
            this.phase = 'analysis'; this.index = 0;
        }
        step() {
            if (this.phase === 'done' || this.game.over) return 'done';
            if (this.index < this.actions.length) {
                this.phase = 'movement';
                const action = this.actions[this.index++]; this.game.action(action); return action;
            }
            this.phase = 'descent';
            if (this.game.move(0, 1)) { this.game.score += 2; return 'descend'; }
            this.game.lock(); this.phase = 'done'; return 'lock';
        }
    }
    const api = {Game, SHAPES, heuristic, analyze, AIPlayback};
    if (typeof module !== 'undefined' && module.exports) module.exports = api;
    else root.TetrisEngine = api;
})(globalThis);
