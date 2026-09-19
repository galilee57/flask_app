(() => {
    'use strict';
    const {Game, SHAPES, heuristic, analyze, AIPlayback} = window.TetrisEngine;
    const $ = id => document.getElementById(id);
    const messages = JSON.parse($('tetris-translations').textContent);
    const locale = document.documentElement.lang === 'en' ? 'en-GB' : 'fr-FR';
    const tr = (message, values = {}) => messages[message].replace(/\{(\w+)\}/g, (_, key) => values[key] ?? `{${key}}`);
    const number = value => value.toLocaleString(locale);
    const decimal = value => value.toLocaleString(locale, {minimumFractionDigits: 1, maximumFractionDigits: 1});
    const colors = {I: '#67e8f9', J: '#818cf8', L: '#fb923c', O: '#fde047', S: '#4ade80', T: '#c084fc', Z: '#fb7185'};
    let game = new Game(), mode = 'human', state = 'ready', last = 0, elapsed = 0;
    let policy = heuristic, agentName = tr("Heuristique de démonstration");
    const speeds = {human: 1, ai: 3};
    let playback = null, analysis = null;
    const records = {human: 0, ai: 0};
    for (const key of Object.keys(records)) {
        try { const value = Number(localStorage.getItem(`tetris.best.${key}`)); if (Number.isFinite(value) && value > 0) records[key] = value; } catch (_) { /* Storage may be disabled. */ }
    }
    function saveBest() {
        if (game.score <= records[mode]) return;
        records[mode] = game.score;
        try { localStorage.setItem(`tetris.best.${mode}`, String(game.score)); } catch (_) { /* Keep session record. */ }
    }
    function cell(ctx, x, y, size, type, ghost = false) {
        ctx.fillStyle = colors[type]; ctx.strokeStyle = colors[type];
        if (ghost) { ctx.globalAlpha = .4; ctx.strokeRect(x * size + 3, y * size + 3, size - 6, size - 6); }
        else {
            ctx.fillRect(x * size + 1, y * size + 1, size - 2, size - 2);
            ctx.fillStyle = '#ffffff45'; ctx.fillRect(x * size + 3, y * size + 3, size - 6, 3);
        }
        ctx.globalAlpha = 1;
    }
    function draw() {
        const ctx = $('tetris-board').getContext('2d'); ctx.clearRect(0, 0, 300, 600);
        ctx.strokeStyle = '#182338'; ctx.lineWidth = 1;
        for (let x = 0; x <= 10; x++) { ctx.beginPath(); ctx.moveTo(x * 30, 0); ctx.lineTo(x * 30, 600); ctx.stroke(); }
        for (let y = 0; y <= 20; y++) { ctx.beginPath(); ctx.moveTo(0, y * 30); ctx.lineTo(300, y * 30); ctx.stroke(); }
        game.board.forEach((row, y) => row.forEach((type, x) => { if (type) cell(ctx, x, y, 30, type); }));
        if (!game.over) {
            const ghost = {...game.piece};
            while (game.valid({...ghost, y: ghost.y + 1})) ghost.y++;
            for (const [piece, shadow] of [[ghost, true], [game.piece, false]]) {
                piece.matrix.forEach((row, y) => row.forEach((v, x) => { if (v) cell(ctx, piece.x + x, piece.y + y, 30, piece.type, shadow); }));
            }
        }
        if (mode === 'ai' && analysis?.best && playback?.phase !== 'done') {
            const target = analysis.best.landing;
            ctx.save(); ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 2; ctx.setLineDash([4, 3]);
            target.matrix.forEach((row, y) => row.forEach((v, x) => {
                if (v) ctx.strokeRect((target.x + x) * 30 + 4, (target.y + y) * 30 + 4, 22, 22);
            })); ctx.restore();
        }
        const next = $('next-piece').getContext('2d'); next.clearRect(0, 0, 112, 80);
        const matrix = SHAPES[game.next];
        next.save(); next.translate((112 - matrix.length * 22) / 2, 8);
        matrix.forEach((row, y) => row.forEach((v, x) => { if (v) cell(next, x, y, 22, game.next); })); next.restore();
        $('next-piece').setAttribute('aria-label', tr("Prochaine pièce : {piece}", {piece: game.next}));
    }
    function render() {
        saveBest();
        $('score').textContent = game.score.toLocaleString(locale); $('lines').textContent = game.lines;
        $('best').textContent = records[mode].toLocaleString(locale);
        $('play').textContent = state === 'running' ? tr("Pause") : state === 'paused' ? tr("Reprendre") : state === 'over' ? tr("Rejouer") : tr("Jouer");
        $('state-label').textContent = {ready: tr("Prêt"), running: tr("En jeu"), paused: tr("Pause"), over: tr("Terminé")}[state];
        $('board-overlay').hidden = state === 'running' || (mode === 'ai' && state === 'paused' && $('ai-manual').checked);
        $('overlay-title').textContent = state === 'over' ? tr("Partie terminée") : state === 'paused' ? tr("On fait une pause") : mode === 'ai' ? tr("La machine est prête") : tr("À toi de jouer");
        $('overlay-description').textContent = state === 'over' ? tr("{score} points · Rejouer pour réessayer", {score: number(game.score)}) : state === 'paused' ? tr("Appuie sur Reprendre pour continuer") : tr("Appuie sur Jouer pour commencer");
        document.querySelectorAll('[data-action]').forEach(button => { button.disabled = mode !== 'human' || state !== 'running'; });
        $('ai-step').disabled = mode !== 'ai' || !$('ai-manual').checked || state === 'over';
        draw();
    }
    function reset(start = false) { saveBest(); game = new Game(); state = start ? 'running' : 'ready'; elapsed = 0; playback = null; analysis = null; $('ai-candidates').replaceChildren(); $('ai-phase').textContent = tr("En attente d’une pièce."); $('ai-reason').textContent = tr("L’IA compare les placements possibles avant de déplacer la pièce."); render(); }
    function toggle() {
        if (state === 'ready' || state === 'over') reset(true);
        else { state = state === 'running' ? 'paused' : 'running'; elapsed = 0; render(); }
        $('status').textContent = state === 'running' ? tr("Partie en cours.") : tr("Partie en pause.");
    }
    function finish() {
        if (game.over) { state = 'over'; $('status').textContent = tr("Partie terminée : {score} points, {lines} lignes.", {score: number(game.score), lines: number(game.lines)}); }
        render();
    }
    function act(action) { if (state !== 'running' || mode !== 'human') return; game.action(action); if (action === 'drop') elapsed = 0; finish(); }
    $('tetris-info-open').addEventListener('click', () => {
        if (state === 'running') { state = 'paused'; elapsed = 0; $('status').textContent = tr("Partie en pause."); render(); }
    });
    $('play').addEventListener('click', () => { toggle(); $('tetris-board').focus({preventScroll: true}); });
    $('restart').addEventListener('click', () => { reset(true); $('tetris-board').focus({preventScroll: true}); $('status').textContent = tr("Nouvelle partie."); });
    document.querySelectorAll('[data-action]').forEach(button => button.addEventListener('click', () => act(button.dataset.action)));
    function describeAgent() {
        $('ai-inspector').hidden = mode !== 'ai';
        updateSpeed();
        $('mode-label').textContent = mode === 'human' ? tr("Mode humain") : tr("Mode IA");
        $('agent-description').textContent = mode === 'human' ? tr("Clavier ou boutons tactiles. Changer de mode remet la partie à zéro.") : tr("{agent}. Le réseau neuronal sera ajouté ultérieurement. Changer de mode remet la partie à zéro.", {agent: agentName});
    }
    document.querySelectorAll('[name="tetris-mode"]').forEach(input => input.addEventListener('change', () => {
        saveBest(); mode = input.value; reset(); describeAgent(); $('status').textContent = tr("Mode changé. Prêt à jouer.");
    }));
    function updateSpeed() {
        $('speed').value = speeds[mode];
        $('speed-label').textContent = mode === 'ai' ? tr("Vitesse IA") : tr("Vitesse humain");
        $('speed-value').textContent = mode === 'ai' ? tr("{seconds} s / étape", {seconds: decimal(stepDelay() / 1000)}) : `${speeds.human}×`;
        $('speed-help').textContent = mode === 'ai' ? tr("Un réglage indépendant : 2 s à 0,2 s par action. Le temps de lecture du choix est trois fois plus long.") : tr("Règle la chute automatique des pièces. Le réglage IA est conservé séparément.");
    }
    function stepDelay() { return mode === 'human' ? 800 / speeds.human : 2200 - 200 * speeds.ai; }
    $('speed').addEventListener('input', () => { speeds[mode] = Number($('speed').value); updateSpeed(); elapsed = 0; });
    $('ai-manual').addEventListener('change', () => { elapsed = 0; render(); });
    $('ai-step').addEventListener('click', () => {
        if (mode !== 'ai' || !$('ai-manual').checked || state === 'over') return;
        if (state === 'ready') state = 'paused';
        aiStep(); elapsed = 0; finish();
    });
    function aiStep() {
        try {
            if (!playback || playback.phase === 'done') {
                analysis = policy === heuristic ? analyze(game.snapshot()) : null;
                const actions = analysis ? analysis.best?.actions || ['drop'] : policy(game.snapshot());
                playback = new AIPlayback(game, actions);
                $('ai-phase').textContent = tr("1 · Comparaison et choix du placement");
                $('ai-candidates').replaceChildren();
                if (analysis?.best) {
                    const best = analysis.best;
                    $('ai-reason').textContent = tr("{count} placements distincts comparés. Choix : colonne {column}, {turns} rotation(s), valeur {value}. {lines} ligne(s), {holes} trou(s), hauteur totale {height}, relief {roughness}.", {count: analysis.candidates.length, column: best.column, turns: best.turns, value: decimal(best.value), lines: best.lines, holes: best.holes, height: best.height, roughness: best.roughness});
                    for (const candidate of analysis.candidates.slice(0, 3)) {
                        const row = document.createElement('tr');
                        for (const value of [`${candidate.column} / ${candidate.turns}`, candidate.lines, candidate.height, candidate.holes, candidate.roughness, decimal(candidate.value)]) {
                            const cell = document.createElement('td'); cell.textContent = value; row.append(cell);
                        }
                        $('ai-candidates').append(row);
                    }
                } else $('ai-reason').textContent = tr("Agent personnalisé : actions affichées, critères de décision non fournis.");
            } else {
                const action = playback.step();
                $('ai-phase').textContent = {left: tr("2 · Déplacement à gauche"), right: tr("2 · Déplacement à droite"), rotate: tr("2 · Rotation horaire"), descend: tr("3 · Descente vers la cible"), lock: tr("4 · Pièce posée, résultat du choix"), done: tr("Placement terminé")}[action];
            }
        } catch (error) {
            playback = null; analysis = null; state = 'paused';
            $('status').textContent = tr("Agent indisponible : vérifie sa politique avant de reprendre.");
            console.error('Tetris AI:', error);
        }
    }
    document.addEventListener('keydown', event => {
        if (!$('tetris-info-dialog').classList.contains('hidden')) return;
        if (event.target.closest('input, select, textarea, button, a, [contenteditable="true"]')) return;
        if (event.code === 'KeyP') { event.preventDefault(); if (!event.repeat) toggle(); return; }
        const action = {ArrowLeft: 'left', ArrowRight: 'right', ArrowUp: 'rotate', ArrowDown: 'down', Space: 'drop'}[event.code];
        if (action && mode === 'human' && state === 'running') { event.preventDefault(); if (!event.repeat || ['left','right','down'].includes(action)) act(action); }
    });
    document.addEventListener('visibilitychange', () => {
        if (document.hidden && state === 'running') { state = 'paused'; elapsed = 0; $('status').textContent = tr("Pause automatique : onglet masqué."); render(); }
    });
    // NN extension: synchronous policy(snapshot) -> bounded list of legal action names.
    // A plan is animated action by action, then descends one cell per step.
    window.TetrisAI = {
        setPolicy(fn, name = tr("Agent personnalisé")) {
            if (typeof fn !== 'function') throw new TypeError(tr("La politique doit être une fonction."));
            policy = fn; agentName = String(name); reset(); describeAgent();
        },
        resetPolicy() { policy = heuristic; agentName = tr("Heuristique de démonstration"); reset(); describeAgent(); },
        getState() { return game.snapshot(); },
    };
    function frame(time) {
        const delta = last ? Math.min(time - last, 100) : 0; last = time;
        if (state === 'running' && !(mode === 'ai' && $('ai-manual').checked)) {
            elapsed += delta;
            const delay = stepDelay() * (mode === 'ai' && ['analysis', 'done'].includes(playback?.phase) ? 3 : 1);
            if (elapsed >= delay) {
                elapsed = 0;
                if (mode === 'human') game.tick(); else aiStep();
                finish();
            }
        }
        requestAnimationFrame(frame);
    }
    updateSpeed(); render(); requestAnimationFrame(frame);
})();
