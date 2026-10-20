// app/projects/prey_predator/src/chart.ts
function chartWindow(history, start, end) {
  return history.filter((s) => s.time >= start && s.time <= end);
}
function chartMaximum(data, visible2) {
  let max = 10;
  for (const s of data) for (const key of visible2) max = Math.max(max, s[key]);
  return max;
}

// app/projects/prey_predator/src/animals.ts
var DIRECTIONS = 8;
var FRAMES = 6;
var SIZE = 72;
var SCALE = 2;
var sprites = /* @__PURE__ */ new Map();
function directionIndex(angle) {
  return (Math.round(angle / (Math.PI / 4)) % DIRECTIONS + DIRECTIONS) % DIRECTIONS;
}
var circularDelta = (to, from) => Math.atan2(Math.sin(to - from), Math.cos(to - from));
var Facing = class {
  direction;
  candidate;
  since;
  lastTime;
  heading;
  constructor(angle, time) {
    this.direction = this.candidate = directionIndex(angle);
    this.heading = angle;
    this.since = this.lastTime = time;
  }
  update(angle, time) {
    const dt = Math.max(0, time - this.lastTime);
    this.lastTime = time;
    this.heading += circularDelta(angle, this.heading) * (1 - Math.exp(-dt / 0.085));
    const distance = Math.abs(circularDelta(this.heading, this.direction * Math.PI / 4));
    const next = distance > Math.PI / 8 + Math.PI / 18 ? directionIndex(this.heading) : this.direction;
    if (next === this.direction) {
      this.candidate = next;
      this.since = time;
    } else if (next !== this.candidate) {
      this.candidate = next;
      this.since = time;
    } else if (time - this.since >= 0.12) {
      this.direction = next;
      this.since = time;
    }
    return this.direction;
  }
};
var facings = /* @__PURE__ */ new WeakMap();
function createFrame(species, direction, frame2) {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = SIZE * SCALE;
  const c = canvas.getContext("2d");
  c.scale(SCALE, SCALE);
  c.translate(SIZE / 2, 43);
  const angle = direction * Math.PI / 4;
  const dx = Math.cos(angle), dy = Math.sin(angle);
  const phase = frame2 / FRAMES * Math.PI * 2;
  const rabbit = species === "prey";
  const stride = Math.sin(phase);
  const bounce = Math.abs(Math.sin(phase)) * (rabbit ? 1.8 : 0.8);
  const front = dy >= -0.1;
  const side = Math.abs(dx) > 0.2;
  const fur = rabbit ? "#f1e6c8" : "#cd7139";
  const light = rabbit ? "#fff5df" : "#ef9a51";
  const shade = rabbit ? "#c8c6a5" : "#9c4d2e";
  const point = (forward, lateral, height = 0) => [
    dx * forward - dy * lateral,
    dy * forward * 0.63 + dx * lateral * 0.63 - height - bounce
  ];
  function oval(x, y, rx, ry, color, rotation = 0) {
    c.fillStyle = color;
    c.beginPath();
    c.ellipse(x, y, rx, ry, rotation, 0, Math.PI * 2);
    c.fill();
  }
  function poly(points, color) {
    c.fillStyle = color;
    c.beginPath();
    points.forEach(([x, y], i) => i ? c.lineTo(x, y) : c.moveTo(x, y));
    c.closePath();
    c.fill();
  }
  function foot(forward, lateral, offset) {
    const move = Math.sin(phase + offset);
    const [x, y] = point(forward + move * 2.3, lateral, Math.max(0, move) * 2);
    if (!rabbit) {
      const [bx2, by2] = point(forward, lateral, 7);
      poly([[bx2 - 1.5, by2], [bx2 + 1.5, by2], [x + 1.7, y], [x - 1.7, y]], shade);
    }
    oval(x, y, rabbit ? 3.5 : 2.5, 1.8, rabbit ? shade : "#593e30");
  }
  function tail() {
    const [x, y] = point(-11, 0, rabbit ? 6 : 8);
    if (rabbit) oval(x, y, 3.8, 3.7, "#fff9e9");
    else {
      const [tx, ty] = point(-24, Math.sin(phase) * 1.5, 7);
      poly([[x - 3, y - 4], [tx - 3, ty - 2], [tx, ty + 3], [x + 3, y + 2]], "#cf713d");
      poly([[tx - 3, ty - 2], [tx, ty + 3], [tx + dx * 6, ty + dy * 3.8 - 1]], "#fff0d1");
    }
  }
  function head() {
    const [hx, hy] = point(rabbit ? 8 : 11, 0, rabbit ? 12 : 13);
    const earSpread = side ? 3 : 4.3;
    const earSway = stride * 0.7;
    for (const sign of [-1, 1]) {
      const ex = hx + sign * earSpread, ey = hy - 4;
      if (rabbit) {
        oval(ex + earSway, ey - 6, 2.2, 7.5, sign === -1 ? shade : light, sign * 0.13 + earSway * 0.04);
        if (front) oval(ex + earSway, ey - 6, 0.85, 4.8, "#dcafa0", sign * 0.13);
      } else {
        poly([[ex - 3.5, ey + 1], [ex + sign * 0.7 + earSway, ey - 9], [ex + 3.5, ey + 1]], shade);
        if (front) poly([[ex - 1.7, ey], [ex + sign * 0.5 + earSway, ey - 5.5], [ex + 1.7, ey]], "#e8af82");
      }
    }
    oval(hx, hy, rabbit ? 6.5 : 7, rabbit ? 6.2 : 6.6, front ? light : fur);
    if (!front && !side) {
      oval(hx, hy + 2, 4.8, 3, fur);
      return;
    }
    const noseX = hx + dx * (rabbit ? 4.5 : 7), noseY = hy + dy * 3.4 + 2;
    if (!rabbit) {
      poly([[hx - 4, hy + 1], [hx + 4, hy + 1], [noseX + 2, noseY + 2], [noseX - 2, noseY + 2]], "#fff0d2");
      oval(noseX, noseY, 1.8, 1.3, "#393a30");
    } else oval(noseX, noseY, 1.1, 0.9, "#c78e84");
    if (!side) {
      oval(hx - 2.8, hy - 0.7, 1, 1.4, "#273d35");
      oval(hx + 2.8, hy - 0.7, 1, 1.4, "#273d35");
    } else {
      oval(hx + Math.sign(dx) * 3.1, hy - 0.7, 1.15, 1.45, "#273d35");
      oval(hx + Math.sign(dx) * 3.3, hy - 1.2, 0.35, 0.4, "#fffdf0");
    }
  }
  const legs = [[-7, -4, 0], [6, -4, Math.PI], [-7, 4, Math.PI], [6, 4, 0]];
  legs.sort((a, b) => point(a[0], a[1])[1] - point(b[0], b[1])[1]);
  legs.slice(0, 2).forEach((l) => foot(l[0], l[1], l[2]));
  if (front) tail();
  else head();
  const [bx, by] = point(0, 0, 7);
  const bodyRotation = Math.atan2(dy * 0.63, dx);
  oval(bx, by, rabbit ? 10 : 12, rabbit ? 6.7 : 6.2, fur, bodyRotation);
  oval(bx - 1, by - 2, rabbit ? 7.2 : 9, 3.4, light, bodyRotation);
  legs.slice(2).forEach((l) => foot(l[0], l[1], l[2]));
  if (front) head();
  else tail();
  return canvas;
}
function drawAnimal(c, a, time, selected2) {
  let facing = facings.get(a);
  if (!facing) {
    facing = new Facing(a.angle, time);
    facings.set(a, facing);
  }
  const direction = facing.update(a.angle, time), key = `${a.species}:${direction}`;
  let frames = sprites.get(key);
  if (!frames) {
    frames = Array.from({ length: FRAMES }, (_, i) => createFrame(a.species, direction, i));
    sprites.set(key, frames);
  }
  const frame2 = Math.floor(time * (a.species === "prey" ? 11 : 9) * a.speed + a.id) % FRAMES;
  c.save();
  c.translate(a.x, a.y);
  c.fillStyle = "#244f3838";
  c.beginPath();
  c.ellipse(-3, 3, a.species === "prey" ? 11 : 15, 4, 0, 0, Math.PI * 2);
  c.fill();
  if (selected2) {
    c.strokeStyle = "#fff8cb";
    c.lineWidth = 2;
    c.beginPath();
    c.ellipse(0, 3, 18, 10, 0, 0, Math.PI * 2);
    c.stroke();
  }
  c.drawImage(frames[frame2], -SIZE / 2, -43, SIZE, SIZE);
  c.restore();
}

// app/projects/prey_predator/src/engine.ts
var defaults = { prey: 65, predators: 9, plants: 260, regrowth: 1, preySpeed: 36, predatorSpeed: 47, metabolism: 1, burrows: 6, burrowCapacity: 5 };
var WIDTH = 1200;
var HEIGHT = 800;
var STEP = 1 / 30;
var MAX_AGENTS = 650;
var Simulation = class {
  constructor(settings = { ...defaults }, seed = 42) {
    this.settings = settings;
    this.seed = seed >>> 0;
    for (let i = 0; i < settings.plants; i++) this.plants.push({ x: 24 + this.random() * (WIDTH - 48), y: 24 + this.random() * (HEIGHT - 48), growth: this.random() });
    for (let i = 0; i < settings.burrows; i++) this.burrows.push({ id: i + 1, x: 130 + i % 3 * 440, y: 130 + Math.floor(i / 3) * 540 / Math.max(1, Math.ceil(settings.burrows / 3) - 1), capacity: settings.burrowCapacity });
    this.add("prey", settings.prey);
    this.add("predator", settings.predators);
    this.sample();
  }
  settings;
  burrows = [];
  agents = [];
  plants = [];
  history = [];
  time = 0;
  births = 0;
  deaths = 0;
  eaten = 0;
  seed;
  nextId = 1;
  lastSample = -1;
  random() {
    this.seed = Math.imul(1664525, this.seed) + 1013904223 >>> 0;
    return this.seed / 4294967296;
  }
  add(species, count = 1, x, y) {
    for (let i = 0; i < count && this.agents.length < MAX_AGENTS; i++) this.agents.push({ id: this.nextId++, species, x: x ?? 40 + this.random() * (WIDTH - 80), y: y ?? 40 + this.random() * (HEIGHT - 80), angle: this.random() * Math.PI * 2, energy: species === "prey" ? 72 : 100, age: 0, cooldown: 8 + this.random() * 12, target: null, state: "Explore", speed: 0.9 + this.random() * 0.2 });
  }
  occupancy(id) {
    return this.agents.filter((a) => a.burrowId === id && a.energy > 0).length;
  }
  setCapacity(id, capacity) {
    const b = this.burrows.find((b2) => b2.id === id);
    if (b) b.capacity = Math.max(this.occupancy(id), Math.min(30, Math.max(0, Math.floor(capacity))));
  }
  tick(dt = STEP) {
    this.time += dt;
    for (const p of this.plants) p.growth = Math.min(1, p.growth + dt * 0.045 * this.settings.regrowth);
    const dead = /* @__PURE__ */ new Set();
    const children = [];
    const alive = this.agents.filter((a) => a.energy > 0);
    for (const a of alive) {
      if (dead.has(a.id)) continue;
      const previousTarget = a.target;
      a.age += dt;
      a.cooldown -= dt;
      a.target = null;
      if (a.burrowId != null) {
        a.energy -= dt * 2.9 * this.settings.metabolism;
        if (a.energy <= 0 || a.age > 210) {
          dead.add(a.id);
          continue;
        }
        const home = this.burrows.find((b) => b.id === a.burrowId);
        const danger = home && alive.some((b) => b.species === "predator" && Math.hypot(b.x - home.x, b.y - home.y) < 150);
        if (home && a.energy > 45 && (this.time < (a.shelterUntil ?? 0) || danger)) {
          a.state = "\xC0 l\u2019abri";
          continue;
        }
        a.burrowId = null;
        a.shelterCooldown = this.time + 8;
        const nearest = home ? alive.filter((b) => b.species === "predator").sort((b, c) => Math.hypot(b.x - home.x, b.y - home.y) - Math.hypot(c.x - home.x, c.y - home.y))[0] : void 0;
        if (home) {
          a.angle = nearest ? Math.atan2(home.y - nearest.y, home.x - nearest.x) : a.angle;
          a.x = Math.max(18, Math.min(WIDTH - 18, home.x + Math.cos(a.angle) * 22));
          a.y = Math.max(18, Math.min(HEIGHT - 18, home.y + Math.sin(a.angle) * 22));
        }
        a.state = "Cherche \xE0 manger";
        continue;
      }
      let tx = a.x + Math.cos(a.angle) * 35, ty = a.y + Math.sin(a.angle) * 35, mult = 1;
      if (a.species === "prey") {
        let threat = alive.find((b) => b.id === previousTarget && b.species === "predator" && !dead.has(b.id) && (a.x - b.x) ** 2 + (a.y - b.y) ** 2 < 145 * 145);
        let best = threat ? ((a.x - threat.x) ** 2 + (a.y - threat.y) ** 2) * 0.64 : 125 * 125;
        for (const b of alive) if (b.species === "predator" && !dead.has(b.id)) {
          const d = (a.x - b.x) ** 2 + (a.y - b.y) ** 2;
          if (d < best) {
            best = d;
            threat = b;
          }
        }
        if (threat) {
          const refuge = a.energy > 45 && this.time >= (a.shelterCooldown ?? 0) ? this.burrows.filter((b) => this.occupancy(b.id) < b.capacity && Math.hypot(b.x - a.x, b.y - a.y) < 240).sort((b, c) => Math.hypot(b.x - a.x, b.y - a.y) - Math.hypot(c.x - a.x, c.y - a.y))[0] : void 0;
          mult = 1.27;
          a.target = threat.id;
          if (refuge) {
            tx = refuge.x;
            ty = refuge.y;
            a.state = "Rejoint un terrier";
            if (Math.hypot(tx - a.x, ty - a.y) < 16) {
              a.burrowId = refuge.id;
              a.shelterUntil = this.time + 4;
              a.x = refuge.x;
              a.y = refuge.y;
              a.state = "\xC0 l\u2019abri";
              a.energy -= dt * 2.9 * this.settings.metabolism;
              continue;
            }
          } else {
            tx = a.x + (a.x - threat.x) * 3;
            ty = a.y + (a.y - threat.y) * 3;
            a.state = "Fuit";
          }
        } else {
          let food, dist = 160 * 160;
          for (const p of this.plants) if (p.growth >= 0.75) {
            const d = (a.x - p.x) ** 2 + (a.y - p.y) ** 2;
            if (d < dist) {
              dist = d;
              food = p;
            }
          }
          if (food) {
            tx = food.x;
            ty = food.y;
            a.state = "Broute";
            if (dist < 15 * 15 && food.growth >= 0.75) {
              food.growth = 0;
              a.energy += 24;
            }
          } else a.state = "Explore";
        }
      } else {
        let victim, dist = 205 * 205;
        for (const b of alive) if (b.species === "prey" && b.burrowId == null && !dead.has(b.id)) {
          const d = (a.x - b.x) ** 2 + (a.y - b.y) ** 2;
          if (d < dist) {
            dist = d;
            victim = b;
          }
        }
        if (victim) {
          tx = victim.x;
          ty = victim.y;
          a.target = victim.id;
          a.state = "Chasse";
          if (dist < 17 * 17) {
            dead.add(victim.id);
            a.energy += 65;
            this.eaten++;
          }
        } else a.state = "Explore";
      }
      if (a.state === "Explore") a.angle += (this.random() - 0.5) * 2.5 * dt;
      else a.angle = Math.atan2(ty - a.y, tx - a.x);
      const speed2 = (a.species === "prey" ? this.settings.preySpeed : this.settings.predatorSpeed) * a.speed * mult;
      a.x += Math.cos(a.angle) * speed2 * dt;
      a.y += Math.sin(a.angle) * speed2 * dt;
      if (a.x < 18 || a.x > WIDTH - 18) {
        a.angle = Math.PI - a.angle;
        a.x = Math.max(18, Math.min(WIDTH - 18, a.x));
      }
      if (a.y < 18 || a.y > HEIGHT - 18) {
        a.angle = -a.angle;
        a.y = Math.max(18, Math.min(HEIGHT - 18, a.y));
      }
      a.energy -= dt * (a.species === "prey" ? 2.9 * mult : 4.1) * this.settings.metabolism;
      if (a.energy <= 0 || a.age > (a.species === "prey" ? 210 : 260)) dead.add(a.id);
      else if (a.energy > (a.species === "prey" ? 112 : 168) && a.cooldown <= 0 && this.agents.length + children.length < MAX_AGENTS) {
        a.energy *= 0.56;
        a.cooldown = a.species === "prey" ? 15 : 25;
        children.push({ species: a.species, x: Math.max(20, Math.min(WIDTH - 20, a.x + 12)), y: Math.max(20, Math.min(HEIGHT - 20, a.y + 12)) });
      }
      a.energy = Math.min(a.energy, 220);
    }
    this.deaths += dead.size;
    this.agents = this.agents.filter((a) => !dead.has(a.id));
    for (const c of children) {
      this.add(c.species, 1, c.x, c.y);
      this.births++;
    }
    if (Math.floor(this.time) > this.lastSample) this.sample();
  }
  sample() {
    this.lastSample = Math.floor(this.time);
    this.history.push({ time: this.time, prey: this.agents.filter((a) => a.species === "prey").length, predators: this.agents.filter((a) => a.species === "predator").length, plants: this.plants.filter((p) => p.growth >= 0.75).length, sheltered: this.agents.filter((a) => a.burrowId != null).length });
    if (this.history.length > 3600) this.history.shift();
  }
};

// app/projects/prey_predator/src/main.ts
var messages = JSON.parse(document.getElementById("pp-text").textContent);
var text = (key) => messages[key] ?? key;
var $ = (id) => document.getElementById(id);
function range(id, label, min, max, value, step = 1) {
  return `<div class="range-row"><label class="range-head" for="${id}">${label}<output id="${id}-value">${value}</output></label><input type="range" id="${id}" min="${min}" max="${max}" value="${value}" step="${step}"></div>`;
}
$("initial").innerHTML = range("initial-prey", text("Proies"), 0, 200, defaults.prey) + range("initial-predators", text("Pr\xE9dateurs"), 0, 50, defaults.predators) + range("initial-plants", text("Touffes de v\xE9g\xE9tation"), 30, 500, defaults.plants) + range("initial-burrows", text("Nombre de terriers"), 0, 12, defaults.burrows) + range("initial-capacity", text("Places par terrier"), 1, 20, defaults.burrowCapacity);
$("parameters").innerHTML = range("regrowth", text("Repousse v\xE9g\xE9tale"), 0, 3, 1, 0.1) + range("preySpeed", text("Vitesse des proies"), 15, 75, 36) + range("predatorSpeed", text("Vitesse des pr\xE9dateurs"), 15, 85, 47) + range("metabolism", text("D\xE9pense \xE9nerg\xE9tique"), 0.3, 2, 1, 0.1);
var chartMode = 180;
var chartStart = 0;
var chartEnd = 0;
var visible = /* @__PURE__ */ new Set(["prey", "predators", "plants", "sheltered"]);
var sim = new Simulation();
var paused = false;
var speed = 1;
var selected = null;
var accumulator = 0;
var last = performance.now();
var uiAt = 0;
var world = $("world");
var ctx = world.getContext("2d");
var chart = $("chart");
var cc = chart.getContext("2d");
var cam = { x: WIDTH / 2, y: HEIGHT / 2, zoom: 1 };
var showVision = false;
var showTrails = false;
var trails = /* @__PURE__ */ new Map();
for (const input of document.querySelectorAll("input[type=range]")) input.oninput = () => {
  if (input.id.startsWith("chart-")) return;
  $(`${input.id}-value`).textContent = input.value;
  if (input.id in sim.settings) sim.settings[input.id] = Number(input.value);
};
function setPause(value) {
  paused = value;
  $("pause").textContent = paused ? text("\u25B6 Reprendre") : text("\u2161 Pause");
  $("live").textContent = paused ? text("Simulation en pause") : text("Simulation active");
}
$("zoom-in").onclick = () => {
  cam.zoom = Math.min(4, cam.zoom * 1.25);
};
$("zoom-out").onclick = () => {
  cam.zoom = Math.max(1, cam.zoom / 1.25);
};
$("pause").onclick = () => setPause(!paused);
$("step").onclick = () => {
  setPause(true);
  sim.tick();
  updateUI();
};
$("speed").onchange = (e) => {
  speed = Number(e.target.value);
};
$("reset").onclick = () => {
  const settings = { ...sim.settings, prey: Number($("initial-prey").value), predators: Number($("initial-predators").value), plants: Number($("initial-plants").value), burrows: Number($("initial-burrows").value), burrowCapacity: Number($("initial-capacity").value) };
  const seed = Number($("seed").value) || 0;
  sim = new Simulation(settings, seed);
  $("season").textContent = `${text("seed")} ${seed >>> 0}`;
  selected = null;
  accumulator = 0;
  trails.clear();
  chartMode = 180;
  chartStart = chartEnd = 0;
  renderBurrows();
  updateUI();
};
$("add-prey").onclick = () => {
  sim.add("prey", 10);
  updateUI();
};
$("add-predator").onclick = () => {
  sim.add("predator", 2);
  updateUI();
};
$("camera").onclick = () => {
  cam.x = WIDTH / 2;
  cam.y = HEIGHT / 2;
  cam.zoom = 1;
};
$("vision").onchange = (e) => showVision = e.target.checked;
$("trails").onchange = (e) => {
  showTrails = e.target.checked;
  trails.clear();
};
$("export").onclick = () => {
  const csv = "time_seconds,prey,predators,vegetation,sheltered_rabbits\n" + sim.history.map((s) => [s.time.toFixed(2), s.prey, s.predators, s.plants, s.sheltered].join(",")).join("\n");
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = "equilibre-populations.csv";
  a.click();
  URL.revokeObjectURL(url);
};
function polygon(points, fill) {
  ctx.fillStyle = fill;
  ctx.beginPath();
  points.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y));
  ctx.closePath();
  ctx.fill();
}
function ellipse(x, y, rx, ry, color) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2);
  ctx.fill();
}
var decorRandom = (n) => {
  const v = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return v - Math.floor(v);
};
var trees = Array.from({ length: 24 }, (_, i) => ({ x: 40 + decorRandom(i + 1) * 1120, y: 55 + decorRandom(i + 71) * 700 }));
function tree(x, y) {
  ellipse(x - 14, y + 8, 29, 10, "#32694535");
  polygon([[x - 3, y], [x + 4, y], [x + 4, y - 35], [x - 3, y - 35]], "#27564a");
  polygon([[x, y - 65], [x - 24, y - 39], [x - 16, y - 13], [x + 12, y - 13], [x + 25, y - 39]], "#215d59");
  polygon([[x, y - 65], [x - 24, y - 39], [x + 2, y - 32]], "#2d7770");
  polygon([[x, y - 65], [x + 25, y - 39], [x + 2, y - 32]], "#8da450");
  polygon([[x - 24, y - 39], [x - 16, y - 13], [x + 2, y - 32]], "#194d50");
}
function animal(a) {
  drawAnimal(ctx, a, sim.time, selected === a.id);
}
function draw() {
  const dpr = Math.min(devicePixelRatio, 2), rect = world.getBoundingClientRect();
  const w = Math.round(rect.width * dpr), h = Math.round(rect.height * dpr);
  if (world.width !== w || world.height !== h) {
    world.width = w;
    world.height = h;
  }
  ctx.setTransform(w / WIDTH, 0, 0, h / HEIGHT, 0, 0);
  ctx.fillStyle = "#739f56";
  ctx.fillRect(0, 0, WIDTH, HEIGHT);
  ctx.translate(WIDTH / 2, HEIGHT / 2);
  ctx.scale(cam.zoom, cam.zoom);
  ctx.translate(-cam.x, -cam.y);
  ctx.fillStyle = "#87b955";
  ctx.fillRect(0, 0, WIDTH, HEIGHT);
  polygon([[0, 0], [530, 0], [210, 800], [0, 800]], "#90bf5c");
  polygon([[780, 0], [1200, 0], [1200, 800], [1050, 800]], "#7fb04e");
  ellipse(602, 400, 100, 54, "#a8c878");
  polygon([[598, 388], [530, 425], [535, 438], [623, 410]], "#38694a35");
  polygon([[590, 388], [617, 388], [626, 401], [583, 401]], "#ded8ac");
  polygon([[596, 388], [596, 327], [605, 309], [605, 388]], "#a9d3b9");
  polygon([[605, 309], [615, 327], [615, 388], [605, 388]], "#5f9f91");
  polygon([[596, 327], [605, 309], [615, 327]], "#f1e4b8");
  for (const b of sim.burrows) {
    ellipse(b.x - 7, b.y + 9, 30, 9, "#42643535");
    ellipse(b.x, b.y, 25, 17, "#9b8050");
    ellipse(b.x, b.y - 4, 22, 14, "#b49c64");
    ellipse(b.x, b.y + 3, 13, 9, "#433c2a");
    ellipse(b.x, b.y + 6, 10, 5, "#292d24");
    ctx.fillStyle = "#fff6dc";
    ctx.font = "11px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(`${sim.occupancy(b.id)}/${b.capacity}`, b.x, b.y + 29);
    ctx.textAlign = "left";
  }
  for (const p of sim.plants) {
    if (p.growth < 0.1) continue;
    const z = p.growth;
    ctx.strokeStyle = p.growth >= 0.75 ? "#3c7740" : "#699648";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(p.x, p.y);
    ctx.lineTo(p.x - 4 * z, p.y - 10 * z);
    ctx.moveTo(p.x, p.y);
    ctx.lineTo(p.x + 4 * z, p.y - 13 * z);
    ctx.moveTo(p.x, p.y);
    ctx.lineTo(p.x, p.y - 15 * z);
    ctx.stroke();
  }
  if (showTrails) for (const a of sim.agents.filter((a2) => a2.burrowId == null)) {
    let path = trails.get(a.id);
    if (!path) {
      path = [];
      trails.set(a.id, path);
    }
    if (!paused) {
      path.push({ x: a.x, y: a.y });
      if (path.length > 55) path.shift();
    }
    ctx.strokeStyle = a.species === "prey" ? "#f7f0bd55" : "#9e452955";
    ctx.lineWidth = 1;
    ctx.beginPath();
    path.forEach((p, i) => i ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y));
    ctx.stroke();
  }
  for (const id of trails.keys()) if (!sim.agents.some((a) => a.id === id)) trails.delete(id);
  const picked = sim.agents.find((a) => a.id === selected);
  if (showVision && picked && picked.burrowId == null) {
    ctx.fillStyle = "#fff7c91a";
    ctx.strokeStyle = "#fff7c970";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(picked.x, picked.y, picked.species === "prey" ? 125 : 205, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    const target = sim.agents.find((a) => a.id === picked.target);
    if (target) {
      ctx.beginPath();
      ctx.moveTo(picked.x, picked.y);
      ctx.lineTo(target.x, target.y);
      ctx.stroke();
    }
  }
  const objects = [...trees.map((t) => ({ y: t.y, draw: () => tree(t.x, t.y) })), ...sim.agents.filter((a) => a.burrowId == null).map((a) => ({ y: a.y, draw: () => animal(a) }))];
  objects.sort((a, b) => a.y - b.y).forEach((o) => o.draw());
  ctx.strokeStyle = "#517844";
  ctx.lineWidth = 8;
  ctx.strokeRect(1, 1, WIDTH - 2, HEIGHT - 2);
}
var seriesColors = { prey: "#507e49", predators: "#d17b4b", plants: "#a9ba69", sheltered: "#568db0" };
function chartDraw() {
  const first = Math.floor(sim.history[0]?.time ?? 0), last2 = Math.ceil(sim.history.at(-1)?.time ?? 0);
  if (chartMode !== "custom") {
    chartEnd = last2;
    chartStart = chartMode === "all" ? first : Math.max(first, last2 - chartMode);
  }
  chartStart = Math.max(first, Math.min(chartStart, last2));
  chartEnd = Math.max(chartStart, Math.min(chartEnd, last2));
  for (const [id, value] of [["start", chartStart], ["end", chartEnd]]) {
    const input = $(`chart-${id}`);
    input.min = String(first);
    input.max = String(Math.max(first + 1, last2));
    input.value = String(value);
    $(`chart-${id}-label`).textContent = `${value} s`;
  }
  document.querySelectorAll("[data-window]").forEach((b2) => b2.classList.toggle("primary", String(chartMode) === b2.dataset.window));
  $("custom-window").classList.toggle("primary", chartMode === "custom");
  const data = chartWindow(sim.history, chartStart, chartEnd), keys = [...visible], max = chartMaximum(data, keys);
  $("chart-range").textContent = `${chartStart}\u2013${chartEnd} s \xB7 ${chartMode === "custom" ? text("P\xE9riode fixe") : text("Suivi en direct")} \xB7 ${data.length} ${text("samples")}${!keys.length ? ` \xB7 ${text("selectSeries")}` : ""}`;
  const r = chart.getBoundingClientRect(), dpr = Math.min(devicePixelRatio, 2);
  chart.width = r.width * dpr;
  chart.height = r.height * dpr;
  cc.setTransform(dpr, 0, 0, dpr, 0, 0);
  const w = r.width, h = r.height, l = 38, b = 22, top = 10;
  cc.font = "10px sans-serif";
  cc.lineWidth = 1;
  for (let i = 0; i < 4; i++) {
    const y = top + (h - b - top) * i / 3;
    cc.strokeStyle = "#e9eddf";
    cc.beginPath();
    cc.moveTo(l, y);
    cc.lineTo(w, y);
    cc.stroke();
    cc.fillStyle = "#8a967e";
    cc.fillText(String(Math.round(max * (1 - i / 3))), 0, y + 3);
  }
  for (const key of keys) {
    cc.strokeStyle = seriesColors[key];
    cc.lineWidth = key === "plants" ? 1.5 : 2.3;
    cc.beginPath();
    for (let i = 0; i < data.length; i++) {
      const sample = data[i], x = l + (sample.time - chartStart) / Math.max(1, chartEnd - chartStart) * (w - l - 4), y = top + (1 - sample[key] / max) * (h - b - top);
      i ? cc.lineTo(x, y) : cc.moveTo(x, y);
      if (data.length === 1) {
        cc.arc(x, y, 2, 0, Math.PI * 2);
      }
    }
    cc.stroke();
  }
  cc.fillStyle = "#8a967e";
  cc.fillText(`${chartStart} s`, l, h - 3);
  cc.fillText(`${chartEnd} s`, w - 45, h - 3);
}
for (const input of document.querySelectorAll("[data-series]")) {
  input.parentElement.style.color = seriesColors[input.dataset.series];
  input.onchange = () => {
    const key = input.dataset.series;
    input.checked ? visible.add(key) : visible.delete(key);
    chartDraw();
  };
}
for (const button of document.querySelectorAll("[data-window]")) button.onclick = () => {
  chartMode = button.dataset.window === "all" ? "all" : Number(button.dataset.window);
  chartDraw();
};
$("custom-window").onclick = () => {
  chartMode = "custom";
  chartDraw();
};
for (const id of ["start", "end"]) $(`chart-${id}`).oninput = () => {
  chartMode = "custom";
  const v = Number($(`chart-${id}`).value);
  if (id === "start") {
    chartStart = v;
    chartEnd = Math.max(v, chartEnd);
  } else {
    chartEnd = v;
    chartStart = Math.min(v, chartStart);
  }
  chartDraw();
};
function renderBurrows() {
  $("burrows").innerHTML = sim.burrows.length ? sim.burrows.map((b) => `<div class="burrow-row"><span>${text("burrow")} ${b.id} <small id="burrow-occupied-${b.id}"></small></span><label>${text("places")} <input aria-label="${text("capacity")} ${b.id}" data-burrow="${b.id}" type="number" min="0" max="30" value="${b.capacity}"></label></div>`).join("") : '<p class="note">Aucun terrier. Ajoutez-en dans les conditions initiales et recommencez.</p>';
  for (const input of document.querySelectorAll("[data-burrow]")) input.onchange = () => {
    sim.setCapacity(Number(input.dataset.burrow), Number(input.value) || 0);
    input.value = String(sim.burrows.find((b) => b.id === Number(input.dataset.burrow)).capacity);
    updateUI();
  };
}
renderBurrows();
function updateUI() {
  for (const b of sim.burrows) {
    $(`burrow-occupied-${b.id}`).textContent = `${sim.occupancy(b.id)} ${text("sheltered")}`;
    const input = document.querySelector(`[data-burrow="${b.id}"]`);
    input.min = String(sim.occupancy(b.id));
  }
  const hidden = sim.agents.filter((a2) => a2.burrowId != null).length;
  $("sheltered-count").textContent = `${hidden} ${text("sheltered")}`;
  const prey = sim.agents.filter((a2) => a2.species === "prey").length, pred = sim.agents.length - prey;
  $("prey").textContent = String(prey);
  $("predators").textContent = String(pred);
  $("plants").textContent = String(sim.plants.filter((p) => p.growth >= 0.75).length);
  $("time").textContent = `${Math.floor(sim.time / 60)}:${String(Math.floor(sim.time % 60)).padStart(2, "0")}`;
  $("status").textContent = `${sim.births} ${text("births")} \xB7 ${sim.deaths} ${text("deaths")} \xB7 ${sim.eaten} ${text("hunted")}${!prey ? text("preyExtinct") : !pred ? text("predatorsExtinct") : ""} \xB7 ${text("history")}`;
  const a = sim.agents.find((a2) => a2.id === selected);
  $("inspector").innerHTML = a ? `<strong>${a.species === "prey" ? text("Proie") : text("Pr\xE9dateur")} #${a.id}</strong><br>${text("behaviour")}: ${text(a.state)}${a.burrowId != null ? `<br>${text("burrow")}: #${a.burrowId}` : ""}<br>${text("age")}: ${a.age.toFixed(1)} s<br>${text("energy")}: ${Math.round(a.energy)}${a.target ? `<br>${text("target")}: #${a.target}` : ""}<div class="energy"><div style="width:${Math.min(100, a.energy / 220 * 100)}%"></div></div>` : selected ? text("Cet individu est mort. S\xE9lectionnez un autre animal.") : text("Cliquez sur un animal pour observer son comportement et son \xE9nergie.");
  chartDraw();
}
var drag = null;
world.onpointerdown = (e) => {
  drag = { x: e.clientX, y: e.clientY, cx: cam.x, cy: cam.y, moved: false };
  world.setPointerCapture(e.pointerId);
};
world.onpointermove = (e) => {
  if (!drag) return;
  const r = world.getBoundingClientRect(), dx = e.clientX - drag.x, dy = e.clientY - drag.y;
  if (Math.hypot(dx, dy) > 4) drag.moved = true;
  if (drag.moved) {
    cam.x = drag.cx - dx / r.width * WIDTH / cam.zoom;
    cam.y = drag.cy - dy / r.height * HEIGHT / cam.zoom;
  }
};
world.onpointerup = (e) => {
  if (drag && !drag.moved) {
    const r = world.getBoundingClientRect(), x = ((e.clientX - r.left) / r.width * WIDTH - WIDTH / 2) / cam.zoom + cam.x, y = ((e.clientY - r.top) / r.height * HEIGHT - HEIGHT / 2) / cam.zoom + cam.y;
    selected = sim.agents.reduce((best, a) => {
      if (a.burrowId != null) return best;
      const d = Math.hypot(a.x - x, a.y - y);
      return d < 25 / cam.zoom && (!best || d < best.d) ? { id: a.id, d } : best;
    }, null)?.id ?? null;
    updateUI();
  }
  drag = null;
};
world.onpointercancel = () => drag = null;
world.addEventListener("wheel", (e) => {
  e.preventDefault();
  cam.zoom = Math.max(1, Math.min(4, cam.zoom * Math.exp(-e.deltaY * 1e-3)));
}, { passive: false });
function frame(now) {
  const elapsed = Math.min((now - last) / 1e3, 0.15);
  last = now;
  if (!paused) {
    accumulator += elapsed * speed;
    let n = 0;
    while (accumulator >= STEP && n < 60) {
      sim.tick();
      accumulator -= STEP;
      n++;
    }
  }
  draw();
  if (now - uiAt > 200) {
    updateUI();
    uiAt = now;
  }
  requestAnimationFrame(frame);
}
document.addEventListener("visibilitychange", () => {
  if (document.hidden) setPause(true);
  last = performance.now();
  accumulator = 0;
});
updateUI();
requestAnimationFrame(frame);
