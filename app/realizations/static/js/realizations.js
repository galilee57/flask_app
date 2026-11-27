(() => {
  const form = document.getElementById('realizations-filters');
  if (!form) return;
  const cards = [...document.querySelectorAll('[data-project]')];
  const grid = document.getElementById('realizations-grid');
  const count = document.getElementById('realizations-count');
  const empty = document.getElementById('realizations-empty');
  const messages = JSON.parse(document.getElementById('realizations-messages').textContent);
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();

  function filter(updateUrl = true) {
    const values = new FormData(form);
    const view = values.get('view');
    const theme = values.get('theme');
    const kind = values.get('kind');
    const query = normalize(values.get('q').trim());
    let visible = 0;
    for (const card of cards) {
      const matchesView = view === 'all' || (view === 'selection' && card.dataset.featured === 'true') || card.dataset.origin === view;
      const matchesTheme = !theme || card.dataset.themes.split(' ').includes(theme);
      card.hidden = !(matchesView && matchesTheme && (!kind || card.dataset.kind === kind) && normalize(card.dataset.search).includes(query));
      if (!card.hidden) visible++;
    }
    grid.dataset.view = view;
    count.textContent = messages[visible === 1 ? 'one' : 'many'].replace('{count}', visible);
    empty.hidden = visible > 0;
    if (updateUrl) {
      const url = new URL(location.href);
      for (const key of ['view', 'theme', 'kind', 'q']) {
        const value = values.get(key);
        if (value) url.searchParams.set(key, value);
        else url.searchParams.delete(key);
      }
      history.replaceState(null, '', url);
    }
  }

  form.addEventListener('input', () => filter());
  form.addEventListener('change', () => filter());
  form.addEventListener('submit', event => { event.preventDefault(); filter(); });
  document.getElementById('realizations-reset').addEventListener('click', event => {
    event.preventDefault();
    form.elements.view.value = 'all';
    form.elements.theme.value = '';
    form.elements.kind.value = '';
    form.elements.q.value = '';
    filter();
    form.elements.q.focus();
  });
  window.addEventListener('popstate', () => {
    const params = new URLSearchParams(location.search);
    const view = params.get('view');
    form.elements.view.value = ['selection', 'all', 'professional', 'personal'].includes(view) ? view : 'all';
    form.elements.theme.value = params.get('theme') || '';
    form.elements.kind.value = params.get('kind') || '';
    form.elements.q.value = params.get('q') || '';
    filter(false);
  });
  filter(false);
})();
