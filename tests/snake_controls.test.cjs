// Run with: node --test tests/snake_controls.test.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync('app/projects/snake/static/js/snake.js', 'utf8');
function setup() {
  const elements = new Map();
  const element = id => {
    if (!elements.has(id)) elements.set(id, {value: id === 'speedSlider' ? '5' : '',
      checked: false, dataset: {}, addEventListener() {}});
    return elements.get(id);
  };
  element('game-canvas').getContext = () => new Proxy({}, {get: () => () => {}});
  const directions = ['left', 'up', 'down', 'right'].map(direction => ({dataset: {direction}, addEventListener() {}}));
  const docEvents = {}, windowEvents = {};
  const document = {hidden: false, getElementById: element,
    querySelector: selector => selector.includes(':checked') ? {value: 'human'} : element(selector),
    querySelectorAll: selector => selector === '[data-direction]' ? directions : [],
    addEventListener: (event, fn) => { docEvents[event] = fn; }};
  const context = vm.createContext({document, window: {addEventListener: (event, fn) => {windowEvents[event] = fn;}},
    console, setTimeout: () => 1, clearTimeout() {}, fetch: () => new Promise(() => {})});
  vm.runInContext(source, context);
  return {context, element, document, docEvents, windowEvents, directions,
    run: code => vm.runInContext(code, context)};
}
test('play toggles pause and hidden tabs stop without resuming automatically', () => {
  const app = setup();
  app.run('startGame()');
  assert.equal(app.element('startGame').textContent, 'Pause');
  app.run('startGame()');
  assert.equal(app.element('playStatus').textContent, 'En pause');
  app.run('startGame()');
  app.document.hidden = true;
  app.docEvents.visibilitychange();
  assert.equal(app.run('gameLoop'), null);
  app.document.hidden = false;
  app.docEvents.visibilitychange();
  assert.equal(app.run('gameLoop'), null);
});
test('touch and keyboard directions respect reversal protection', () => {
  const app = setup();
  app.run('chooseDirection("left")');
  assert.equal(app.run('currentDirection'), 'right');
  app.run('chooseDirection("up")');
  assert.equal(app.run('currentDirection'), 'up');
  app.windowEvents.keydown({key: 'ArrowLeft', target: {tagName: 'BUTTON'}, preventDefault() {}});
  assert.equal(app.run('currentDirection'), 'left');
  app.windowEvents.keydown({key: 'ArrowDown', target: {tagName: 'INPUT'}, preventDefault() {}});
  assert.equal(app.run('currentDirection'), 'left');
});
test('offline pauses; token appears only after opting in', () => {
  const app = setup();
  assert.equal(app.element('recordTokenControls').hidden, true);
  app.element('recordStats').checked = true;
  app.run('updateSpeedLabel(); startGame()');
  assert.equal(app.element('recordTokenControls').hidden, false);
  app.windowEvents.offline();
  assert.equal(app.run('gameLoop'), null);
  assert.match(app.element('playStatus').textContent, /Connexion interrompue/);
});
