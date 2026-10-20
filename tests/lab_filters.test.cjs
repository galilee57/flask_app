const { test } = require('node:test');
const assert = require('node:assert/strict');
const { matchesProject } = require('../app/main/static/js/lab.js');
const project = { text: 'Proies & prédateurs Explorer un écosystème vivant', categories: ['simulation', 'javascript'] };
test('search ignores case, accents and word order', () => {
  assert.equal(matchesProject(project, 'all', ' ECOSYSTEME   PREDATEURS '), true);
  assert.equal(matchesProject(project, 'all', 'neige'), false);
});
test('search and exact category filter combine', () => {
  assert.equal(matchesProject(project, 'simulation', 'proies'), true);
  assert.equal(matchesProject(project, 'ai', 'proies'), false);
  assert.equal(matchesProject(project, 'java', ''), false);
  assert.equal(matchesProject(project, 'all', ''), true);
});
