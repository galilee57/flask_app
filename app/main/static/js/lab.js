(function () {
  'use strict';
  function normalize(value) {
    return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  }
  function matchesProject(project, category, query) {
    const words = normalize(query).split(/\s+/).filter(Boolean);
    const text = normalize(project.text);
    return (category === 'all' || project.categories.includes(category)) && words.every(word => text.includes(word));
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = { matchesProject };
  if (typeof document === 'undefined') return;
  const lab = document.getElementById('lab');
  if (!lab) return;
  const search = lab.querySelector('#lab-search');
  const buttons = [...lab.querySelectorAll('[data-action]')];
  const cards = [...lab.querySelectorAll('.carte-wrapper')].map(element => ({
    element,
    categories: element.dataset.categories.split(',').map(normalize),
    text: element.querySelector('[data-project-title]').textContent + ' ' + element.querySelector('[data-project-description]').textContent,
  }));
  const labels = JSON.parse(lab.querySelector('#lab-text').textContent);
  let category = 'all';
  function render() {
    let count = 0;
    cards.forEach(card => {
      const visible = matchesProject(card, category, search.value);
      card.element.hidden = !visible;
      if (visible) count++;
    });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.action === category)));
    lab.querySelector('#lab-count').textContent = `${count} ${count === 1 ? labels.one : labels.many}`;
    lab.querySelector('#lab-empty').hidden = count > 0;
  }
  buttons.forEach(button => button.addEventListener('click', () => { category = button.dataset.action; render(); }));
  search.addEventListener('input', render);
  lab.querySelector('#lab-reset').addEventListener('click', () => {
    category = 'all'; search.value = ''; render(); search.focus();
  });
  render();
})();
