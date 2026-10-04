(() => {
  'use strict';
  const $ = id => document.getElementById(`sp-${id}`);
  const root = document.getElementById('shortest-path-app');
  const text = JSON.parse($('text').textContent);
  let data = null, index = -1, timer = null, requestId = 0;
  const number = value => new Intl.NumberFormat(document.documentElement.lang, {maximumFractionDigits: 2}).format(value);
  function pause() { clearTimeout(timer); timer = null; $('play').textContent = text.play; }
  function choices() {
    const size = Number($('dataset').value);
    for (const key of ['start', 'goal']) {
      $(key).replaceChildren(...Array.from({length: size}, (_, i) => new Option(String(i), String(i))));
    }
    $('goal').value = '1';
  }
  function svgElement(tag, attrs) {
    const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [key, value] of Object.entries(attrs)) element.setAttribute(key, value);
    return element;
  }
  function draw() {
    const svg = $('graph'); svg.replaceChildren();
    if (!data) return;
    const step = data.steps[index];
    const finished = index === data.steps.length - 1;
    const path = finished ? data.path : [];
    const pathEdges = new Set(path.slice(1).map((id, i) => [id, path[i]].sort((a,b) => a-b).join('-')));
    const xs = data.nodes.map(n => n.x), ys = data.nodes.map(n => n.y);
    const minX = Math.min(...xs), minY = Math.min(...ys);
    const width = Math.max(...xs) - minX, height = Math.max(...ys) - minY;
    const scale = Math.min(704 / (width || 1), 464 / (height || 1));
    const positions = new Map(data.nodes.map(n => [n.id, {x: (n.x-minX)*scale + (800-width*scale)/2, y: (n.y-minY)*scale + (560-height*scale)/2}]));
    for (const edge of data.edges) {
      const a = positions.get(edge.source), b = positions.get(edge.target);
      const highlighted = pathEdges.has([edge.source, edge.target].sort((a,b) => a-b).join('-'));
      const line = svgElement('line', {x1: a.x, y1: a.y, x2: b.x, y2: b.y, class: highlighted ? 'path-edge' : 'edge'});
      const title = svgElement('title', {}); title.textContent = `${edge.source} ↔ ${edge.target}: ${number(edge.weight)}`; line.append(title); svg.append(line);
    }
    for (const node of data.nodes) {
      const p = positions.get(node.id);
      let state = step?.visited.includes(node.id) ? 'visited' : step?.frontier.includes(node.id) ? 'frontier' : 'idle';
      if (path.includes(node.id)) state = 'path';
      if (node.id === Number($('start').value)) state = 'start';
      if (node.id === Number($('goal').value)) state = 'goal';
      const group = svgElement('g', {});
      group.append(svgElement('circle', {cx:p.x, cy:p.y, r:data.nodes.length > 73 ? 4 : 10, class:`node ${state}${step?.current === node.id ? ' current' : ''}`}));
      const title = svgElement('title', {}); title.textContent = String(node.id); group.append(title);
      if (data.nodes.length <= 73) {
        const label = svgElement('text', {x:p.x, y:p.y-15, class:'node-label'}); label.textContent = node.id; group.append(label);
      }
      svg.append(group);
    }
    $('count').textContent = step ? step.visited.length : 0;
    $('cost').textContent = finished && data.cost !== null ? number(data.cost) : '—';
    $('scores').textContent = step ? `g = ${number(step.g)} · h = ${number(step.h)} · f = ${number(step.f)}` : 'g = 0 · h = 0 · f = 0';
    $('route').textContent = path.join(' → ');
    $('status').textContent = finished ? (data.path.length ? text.done : text.none) : step ? text.step + step.current : text.ready;
    $('step').disabled = finished; $('play').disabled = finished;
  }
  async function load() {
    pause(); data = null; index = -1;
    const version = ++requestId;
    $('graph').replaceChildren(); $('count').textContent = '0'; $('cost').textContent = '—'; $('route').textContent = ''; $('scores').textContent = '—';
    $('play').disabled = true; $('step').disabled = true; $('status').textContent = text.loading;
    const params = new URLSearchParams({graph:$('dataset').value, start:$('start').value, goal:$('goal').value, algorithm:$('algorithm').value});
    try {
      const response = await fetch(`${root.dataset.url}?${params}`);
      if (!response.ok) throw new Error('request_failed');
      const result = await response.json();
      if (version !== requestId) return;
      data = result; draw();
    } catch (_) { if (version === requestId) $('status').textContent = text.error; }
  }
  function advance() {
    if (!data || index >= data.steps.length-1) return;
    index++; draw();
    if (index === data.steps.length-1) pause();
  }
  function tick() {
    advance();
    if (data && index < data.steps.length-1) timer = setTimeout(tick, Number($('speed').value));
  }
  $('play').addEventListener('click', () => {
    if (timer !== null) { pause(); return; }
    $('play').textContent = text.pause;
    timer = setTimeout(tick, 0);
  });
  $('step').addEventListener('click', () => { pause(); advance(); });
  $('reset').addEventListener('click', load);
  $('dataset').addEventListener('change', () => { choices(); load(); });
  for (const key of ['start', 'goal', 'algorithm']) $(key).addEventListener('change', load);
  document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
  document.getElementById('shortest-path-info-open').addEventListener('click', pause);
  choices(); load();
})();
