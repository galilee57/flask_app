import type { Agent } from './engine';

// Eight upright views, each with six walk frames. Only the ground projection
// changes direction: animals never rotate sideways or upside down on screen.
const DIRECTIONS = 8;
const FRAMES = 6;
const SIZE = 72;
const SCALE = 2;
const sprites = new Map<string, HTMLCanvasElement[]>();

export function directionIndex(angle: number): number {
  return ((Math.round(angle / (Math.PI / 4)) % DIRECTIONS) + DIRECTIONS) % DIRECTIONS;
}

const circularDelta = (to: number, from: number) => Math.atan2(Math.sin(to-from), Math.cos(to-from));

/** Simulation time, rather than rendered frames, controls orientation changes. */
export class Facing {
  direction: number;
  private candidate: number;
  private since: number;
  private lastTime: number;
  private heading: number;
  constructor(angle: number, time: number) {
    this.direction = this.candidate = directionIndex(angle);
    this.heading = angle;
    this.since = this.lastTime = time;
  }
  update(angle: number, time: number): number {
    const dt = Math.max(0, time-this.lastTime);
    this.lastTime = time;
    // Filter tiny heading corrections, including across the -π / π seam.
    this.heading += circularDelta(angle,this.heading)*(1-Math.exp(-dt/0.085));
    const distance = Math.abs(circularDelta(this.heading,this.direction*Math.PI/4));
    // An extra 10° dead band prevents alternating at the edge of two views.
    const next = distance > Math.PI/8 + Math.PI/18 ? directionIndex(this.heading) : this.direction;
    if(next===this.direction){this.candidate=next;this.since=time;}
    else if(next!==this.candidate){this.candidate=next;this.since=time;}
    else if(time-this.since>=0.12){this.direction=next;this.since=time;}
    return this.direction;
  }
}
const facings = new WeakMap<Agent,Facing>();

function createFrame(species: Agent['species'], direction: number, frame: number) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = SIZE * SCALE;
  const c = canvas.getContext('2d')!;
  c.scale(SCALE, SCALE);
  c.translate(SIZE / 2, 43);
  const angle = direction * Math.PI / 4;
  const dx = Math.cos(angle), dy = Math.sin(angle);
  const phase = frame / FRAMES * Math.PI * 2;
  const rabbit = species === 'prey';
  const stride = Math.sin(phase);
  const bounce = Math.abs(Math.sin(phase)) * (rabbit ? 1.8 : .8);
  const front = dy >= -.1;
  const side = Math.abs(dx) > .2;
  const fur = rabbit ? '#f1e6c8' : '#cd7139';
  const light = rabbit ? '#fff5df' : '#ef9a51';
  const shade = rabbit ? '#c8c6a5' : '#9c4d2e';
  const point = (forward: number, lateral: number, height = 0): [number, number] => [
    dx * forward - dy * lateral,
    dy * forward * .63 + dx * lateral * .63 - height - bounce,
  ];
  function oval(x: number, y: number, rx: number, ry: number, color: string, rotation = 0) {
    c.fillStyle = color; c.beginPath(); c.ellipse(x, y, rx, ry, rotation, 0, Math.PI * 2); c.fill();
  }
  function poly(points: [number, number][], color: string) {
    c.fillStyle = color; c.beginPath(); points.forEach(([x,y], i) => i ? c.lineTo(x,y) : c.moveTo(x,y)); c.closePath(); c.fill();
  }
  function foot(forward: number, lateral: number, offset: number) {
    const move = Math.sin(phase + offset);
    const [x,y] = point(forward + move * 2.3, lateral, Math.max(0,move) * 2);
    if (!rabbit) {
      const [bx,by] = point(forward, lateral, 7);
      poly([[bx-1.5,by],[bx+1.5,by],[x+1.7,y],[x-1.7,y]],shade);
    }
    oval(x,y, rabbit ? 3.5 : 2.5, 1.8, rabbit ? shade : '#593e30');
  }
  function tail() {
    const [x,y] = point(-11,0, rabbit ? 6 : 8);
    if(rabbit) oval(x,y,3.8,3.7,'#fff9e9');
    else {
      const [tx,ty] = point(-24,Math.sin(phase)*1.5,7);
      poly([[x-3,y-4],[tx-3,ty-2],[tx,ty+3],[x+3,y+2]],'#cf713d');
      poly([[tx-3,ty-2],[tx,ty+3],[tx+dx*6,ty+dy*3.8-1]],'#fff0d1');
    }
  }
  function head() {
    const [hx,hy] = point(rabbit ? 8 : 11,0,rabbit ? 12 : 13);
    const earSpread = side ? 3 : 4.3;
    const earSway = stride * .7;
    for(const sign of [-1,1]) {
      const ex=hx+sign*earSpread, ey=hy-4;
      if(rabbit) {
        oval(ex+earSway,ey-6,2.2,7.5, sign===-1?shade:light,sign*.13+earSway*.04);
        if(front) oval(ex+earSway,ey-6, .85,4.8,'#dcafa0',sign*.13);
      } else {
        poly([[ex-3.5,ey+1],[ex+sign*.7+earSway,ey-9],[ex+3.5,ey+1]],shade);
        if(front) poly([[ex-1.7,ey],[ex+sign*.5+earSway,ey-5.5],[ex+1.7,ey]],'#e8af82');
      }
    }
    oval(hx,hy,rabbit?6.5:7,rabbit?6.2:6.6,front?light:fur);
    if (!front && !side) {
      // Back view: ears and nape, with no face visible through the skull.
      oval(hx,hy+2,4.8,3,fur);
      return;
    }
    const noseX=hx+dx*(rabbit?4.5:7), noseY=hy+dy*3.4+2;
    if(!rabbit) {
      poly([[hx-4,hy+1],[hx+4,hy+1],[noseX+2,noseY+2],[noseX-2,noseY+2]],'#fff0d2');
      oval(noseX,noseY,1.8,1.3,'#393a30');
    } else oval(noseX,noseY,1.1,.9,'#c78e84');
    if(!side) {
      oval(hx-2.8,hy-.7,1,1.4,'#273d35');
      oval(hx+2.8,hy-.7,1,1.4,'#273d35');
    } else {
      oval(hx+Math.sign(dx)*3.1,hy-.7,1.15,1.45,'#273d35');
      oval(hx+Math.sign(dx)*3.3,hy-1.2,.35,.4,'#fffdf0');
    }
  }
  // Depth sorting of body parts creates distinct front, back and diagonal views.
  const legs = [[-7,-4,0],[6,-4,Math.PI],[-7,4,Math.PI],[6,4,0]];
  legs.sort((a,b)=>point(a[0],a[1])[1]-point(b[0],b[1])[1]);
  legs.slice(0,2).forEach(l=>foot(l[0],l[1],l[2]));
  if(front) tail(); else head();
  const [bx,by] = point(0,0,7);
  const bodyRotation = Math.atan2(dy*.63,dx);
  oval(bx,by,rabbit?10:12,rabbit?6.7:6.2,fur,bodyRotation);
  oval(bx-1,by-2,rabbit?7.2:9,3.4,light,bodyRotation);
  legs.slice(2).forEach(l=>foot(l[0],l[1],l[2]));
  if(front) head(); else tail();
  return canvas;
}

export function drawAnimal(c: CanvasRenderingContext2D, a: Agent, time: number, selected: boolean) {
  let facing=facings.get(a);
  if(!facing){facing=new Facing(a.angle,time);facings.set(a,facing);}
  const direction=facing.update(a.angle,time),key=`${a.species}:${direction}`;
  let frames=sprites.get(key);
  if(!frames){frames=Array.from({length:FRAMES},(_,i)=>createFrame(a.species,direction,i));sprites.set(key,frames);}
  const frame=Math.floor(time*(a.species==='prey'?11:9)*a.speed+a.id)%FRAMES;
  c.save();c.translate(a.x,a.y);
  c.fillStyle='#244f3838';c.beginPath();c.ellipse(-3,3,a.species==='prey'?11:15,4,0,0,Math.PI*2);c.fill();
  if(selected){c.strokeStyle='#fff8cb';c.lineWidth=2;c.beginPath();c.ellipse(0,3,18,10,0,0,Math.PI*2);c.stroke();}
  c.drawImage(frames[frame],-SIZE/2,-43,SIZE,SIZE);
  c.restore();
}
