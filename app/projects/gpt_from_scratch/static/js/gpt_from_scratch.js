(() => {
  'use strict';
  const $ = id => document.getElementById(`gpt-${id}`);
  const demo = $('demo');
  if (!demo) return;
  const words = JSON.parse($('i18n').textContent);
  let models = [];
  function chart(model) {
    const rows = model.metrics;
    const svg = $('chart');
    svg.replaceChildren();
    if (!rows.length) return;
    const ns = 'http://www.w3.org/2000/svg';
    const node = (tag, attrs, text) => {
      const el = document.createElementNS(ns, tag);
      Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, value));
      if (text !== undefined) el.textContent = text;
      svg.append(el); return el;
    };
    const maximum = Math.max(...rows.flatMap(r => [r.train_loss, r.val_loss]), 0.1) * 1.05;
    const last = Math.max(...rows.map(r => r.step), 1);
    const x = step => 55 + step / last * 720;
    const y = loss => 255 - loss / maximum * 225;
    for (let i = 0; i <= 4; i++) {
      const value = maximum * i / 4;
      node('line', {x1:55, x2:775, y1:y(value), y2:y(value), stroke:'#e5e7eb'});
      node('text', {x:45, y:y(value)+4, 'text-anchor':'end', 'font-size':12}, value.toFixed(2));
      const step = last * i / 4;
      node('text', {x:x(step), y:280, 'text-anchor':'middle', 'font-size':12}, Math.round(step));
    }
    for (const [key, color] of [['train_loss','#2563eb'], ['val_loss','#d97706']]) {
      node('polyline', {points:rows.map(r => `${x(r.step)},${y(r[key])}`).join(' '), fill:'none', stroke:color, 'stroke-width':2});
    }
    const best = rows.reduce((a, b) => a.val_loss <= b.val_loss ? a : b);
    node('circle', {cx:x(best.step), cy:y(best.val_loss), r:5, fill:'#d97706', stroke:'#111827'});
    $('metrics').replaceChildren(...rows.map(row => {
      const tr = document.createElement('tr');
      [row.step, row.train_loss.toFixed(4), row.val_loss.toFixed(4)].forEach(value => {
        const td = document.createElement('td'); td.textContent = value; tr.append(td);
      }); return tr;
    }));
  }
  function selectModel() {
    const model = models.find(m => m.id === $('model').value);
    if (!model) return;
    const a = model.architecture;
    $('details').textContent = `${words.language}: ${words[model.language] || model.language} · ${model.parameters ?? '—'} ${words.parameters} · ${model.tokenizer} · ${words.context}: ${a.block_size} tokens · ${a.num_layers} ${words.layers} · ${a.num_heads} ${words.heads} · ${words.corpus}: ${model.corpus_characters ?? '—'} ${words.characters} · ${model.max_steps} ${words.steps} · LR ${model.learning_rate}`;
    chart(model);
  }
  $('model').addEventListener('change', selectModel);
  $('form').addEventListener('submit', async event => {
    event.preventDefault();
    $('submit').disabled = true;
    $('status').textContent = words.working;
    $('prefix').textContent = '';
    $('continuation').textContent = '';
    const prompt = $('prompt').value;
    try {
      const response = await fetch(demo.dataset.generate, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({model:$('model').value, prompt, temperature:Number($('temperature').value), tokens:Number($('tokens').value), seed:Number($('seed').value)})});
      const data = await response.json();
      if (!response.ok) {
        $('status').textContent = words[data.error] || words.invalid;
        return;
      }
      $('prefix').textContent = prompt;
      $('continuation').textContent = data.continuation;
      $('status').textContent = `${words.done} ${data.seconds} ${words.seconds}`;
    } catch (_) { $('status').textContent = words.unavailable; }
    finally { $('submit').disabled = false; }
  });
  async function init() {
    $('status').textContent = words.loading;
    try {
      const response = await fetch(demo.dataset.models);
      if (!response.ok) throw new Error('catalog');
      models = await response.json();
      models.forEach(model => {
        const option = document.createElement('option');
        option.value = model.id; option.textContent = `${model.id.replaceAll('_', ' ')} (${words[model.language] || model.language})`;
        $('model').append(option);
      });
      selectModel(); $('submit').disabled = !models.length;
      $('status').textContent = models.length ? words.ready : words.empty;
    } catch (_) { $('status').textContent = words.unavailable; }
  }
  init();
})();
