const {test} = require('node:test');
const assert = require('node:assert/strict');
const {Game, heuristic} = require('../app/projects/tetris/static/js/engine.js');

test('bag distributes every tetromino once', () => {
    const game = new Game();
    const pieces = [game.piece.type, game.next];
    for (let i = 0; i < 5; i++) pieces.push(game.draw());
    assert.equal(new Set(pieces).size, 7);
});
test('walls, floor and occupied cells reject movement', () => {
    const game = new Game();
    game.piece = {type:'O', matrix:[[1,1],[1,1]], x:0, y:18};
    assert.equal(game.move(-1,0), false);
    assert.equal(game.move(0,1), false);
    game.board[18][2] = 'I';
    assert.equal(game.move(1,0), false);
});
test('four lines award 800 points and compact the board', () => {
    const game = new Game();
    for (let y = 16; y < 20; y++) game.board[y] = Array.from({length:10}, (_,x) => x === 4 ? null : 'J');
    game.piece = {type:'I', matrix:[[1],[1],[1],[1]], x:4, y:16};
    game.lock();
    assert.equal(game.lines, 4); assert.equal(game.score, 800);
    assert.ok(game.board.every(row => row.every(v => v === null)));
});
test('hard drop scores distance and spawns a new piece', () => {
    const game = new Game(); const next = game.next;
    game.piece = {type:'O', matrix:[[1,1],[1,1]], x:4, y:0};
    game.action('drop');
    assert.equal(game.score, 36); assert.equal(game.piece.type, next);
    assert.equal(game.board[19][4], 'O');
});
test('rotation kicks away from the wall', () => {
    const game = new Game();
    game.piece = {type:'T', matrix:[[0,1,0],[0,1,1],[0,1,0]], x:-1, y:3};
    assert.ok(game.valid(game.piece)); assert.ok(game.turn()); assert.ok(game.valid(game.piece));
});
test('blocked spawn ends the game and further actions are ignored', () => {
    const game = new Game(); game.board[0].fill('O'); game.board[1].fill('O'); game.spawn();
    assert.equal(game.over, true); const before = game.snapshot();
    game.action('drop'); game.tick(); assert.deepEqual(game.snapshot(), before);
});
test('agent clears lines without mutating observations', () => {
    const game = new Game(() => .42);
    for (let i = 0; i < 100 && !game.over; i++) {
        const observation = game.snapshot(), original = JSON.stringify(observation);
        const actions = heuristic(observation);
        assert.equal(JSON.stringify(observation), original);
        actions.forEach(action => game.action(action));
        assert.equal(game.board.length, 20);
    }
    assert.ok(game.lines > 0);
});

test('explanation ranks distinct placements using the displayed formula', () => {
    const {analyze} = require('../app/projects/tetris/static/js/engine.js');
    const game = new Game(() => .42), snapshot = game.snapshot();
    const report = analyze(snapshot);
    assert.deepEqual(game.snapshot(), snapshot);
    assert.ok(report.candidates.length > 1);
    for (const c of report.candidates) {
        assert.equal(c.value, c.lines * 8 - c.height * .5 - c.holes * 7 - c.roughness * .3 - (c.over ? 10000 : 0));
        assert.ok(c.value <= report.best.value);
    }
    assert.deepEqual(report.best.actions, heuristic(snapshot));
});
test('animated playback executes one move per step and matches a hard drop', () => {
    const {AIPlayback} = require('../app/projects/tetris/static/js/engine.js');
    const game = new Game(() => .42), reference = new Game(() => .42);
    const actions = ['left', 'rotate', 'drop'];
    const playback = new AIPlayback(game, actions);
    assert.equal(playback.phase, 'analysis');
    const x = game.piece.x;
    assert.equal(playback.step(), 'left'); assert.equal(game.piece.x, x - 1);
    assert.equal(playback.step(), 'rotate');
    assert.equal(playback.step(), 'descend');
    for (let i = 0; i < 25 && playback.phase !== 'done'; i++) playback.step();
    actions.forEach(a => reference.action(a));
    assert.deepEqual(game.snapshot(), reference.snapshot());
    assert.equal(playback.step(), 'done');
    assert.deepEqual(game.snapshot(), reference.snapshot());
    assert.throws(() => new AIPlayback(game, ['invalid']));
});
