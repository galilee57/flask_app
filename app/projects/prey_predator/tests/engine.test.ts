import { test } from 'node:test';
import assert from 'node:assert/strict';
import { Simulation, defaults, MAX_AGENTS, WIDTH, HEIGHT } from '../src/engine.ts';
test('une même graine produit la même expérience',()=>{const a=new Simulation({...defaults},123),b=new Simulation({...defaults},123);for(let i=0;i<900;i++){a.tick();b.tick();}assert.deepEqual(a.agents,b.agents);assert.deepEqual(a.history,b.history);});
test('un milieu sans ressource conduit à la famine',()=>{const s=new Simulation({...defaults,plants:0,predators:0,prey:8});for(let i=0;i<1800;i++)s.tick();assert.equal(s.agents.length,0);assert.equal(s.deaths,8);});
test('la prédation consomme une proie une seule fois',()=>{const s=new Simulation({...defaults,plants:0,prey:0,predators:0,burrows:0});s.add('prey',1,200,200);s.add('predator',2,200,200);s.tick();assert.equal(s.eaten,1);assert.equal(s.deaths,1);assert.equal(s.agents.length,2);});
test('population bornée, positions et énergie finies sur une longue expérience',()=>{const s=new Simulation();for(let i=0;i<9000;i++)s.tick();assert.ok(s.agents.length<=MAX_AGENTS);for(const a of s.agents){assert.ok(Number.isFinite(a.energy));assert.ok(a.x>=18&&a.x<=WIDTH-18);assert.ok(a.y>=18&&a.y<=HEIGHT-18);}for(const p of s.plants)assert.ok(p.growth>=0&&p.growth<=1);});

import { Facing } from '../src/animals.ts';
test('les oscillations autour de la frontière de deux vues ne font pas trembler le sprite',()=>{
  const f=new Facing(0,0);
  for(let i=1;i<=120;i++)assert.equal(f.update(Math.PI/8+(i%2? .04:-.04),i/60),0);
});
test('une vraie réorientation est appliquée rapidement et reste stable',()=>{
  const f=new Facing(0,0);
  for(let i=1;i<=30;i++)f.update(Math.PI/2,i/60);
  assert.equal(f.direction,2);
  for(let i=31;i<90;i++)assert.equal(f.update(Math.PI/2+(i%2?.02:-.02),i/60),2);
});
test('la jonction des angles et la pause ne provoquent pas de changement de vue',()=>{
  const f=new Facing(Math.PI-.01,0);
  for(let i=1;i<=60;i++)assert.equal(f.update(-Math.PI+.01,i/60),4);
  for(let i=0;i<60;i++)assert.equal(f.update(0,1),4);
});
test('la fuite conserve le prédateur courant face à une menace presque équivalente',()=>{
  const s=new Simulation({...defaults,plants:0,prey:0,predators:0,burrows:0});
  s.add('prey',1,500,400);s.add('predator',1,450,400);s.add('predator',1,551,400);
  const rabbit=s.agents[0];rabbit.target=s.agents[1].id;
  s.tick();assert.equal(rabbit.target,s.agents[1].id);
  s.agents[2].x=rabbit.x+49;
  s.tick();assert.equal(rabbit.target,s.agents[1].id);
});

test('un terrier ne dépasse pas sa capacité et protège ses occupants',()=>{
  const s=new Simulation({...defaults,plants:0,prey:0,predators:0,burrows:1,burrowCapacity:1});
  const b=s.burrows[0];s.add('prey',2,b.x,b.y);s.add('predator',1,b.x+60,b.y);
  s.tick();assert.equal(s.occupancy(b.id),1);
  const hidden=s.agents.find(a=>a.burrowId===b.id)!;
  s.agents.find(a=>a.species==='predator')!.x=b.x;
  const before=hidden.energy;s.tick();assert.ok(s.agents.includes(hidden));assert.ok(hidden.energy<before);assert.equal(s.occupancy(b.id),1);
  s.setCapacity(b.id,0);assert.equal(b.capacity,1);
});
test('un lapin affamé quitte le terrier même en présence de danger',()=>{
  const s=new Simulation({...defaults,plants:0,prey:0,predators:0,burrows:1});const b=s.burrows[0];s.add('prey',1,b.x,b.y);s.add('predator',1,b.x+80,b.y);
  const a=s.agents[0];a.burrowId=b.id;a.energy=44;a.shelterUntil=100;s.tick();assert.equal(a.burrowId,null);assert.equal(s.occupancy(b.id),0);assert.ok(a.shelterCooldown!>s.time);
});
test('la faim tue aussi dans un terrier et libère la place',()=>{
  const s=new Simulation({...defaults,plants:0,prey:0,predators:0,burrows:1});s.add('prey',1);s.agents[0].burrowId=1;s.agents[0].energy=.01;s.tick();assert.equal(s.agents.length,0);assert.equal(s.deaths,1);assert.equal(s.occupancy(1),0);
});
import { chartWindow,chartMaximum } from '../src/chart.ts';
test('le graphique filtre la période et adapte son échelle aux séries visibles',()=>{
  const history=[0,1,2,3].map(time=>({time,prey:20,predators:5,plants:100,sheltered:3}));
  assert.deepEqual(chartWindow(history,1,2).map(s=>s.time),[1,2]);
  assert.equal(chartMaximum(history,['predators','sheltered']),10);assert.equal(chartMaximum(history,['plants']),100);assert.deepEqual(chartWindow(history,9,10),[]);assert.equal(chartMaximum(history,[]),10);
});
