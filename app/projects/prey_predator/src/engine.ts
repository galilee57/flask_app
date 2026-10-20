export type Species = 'prey' | 'predator';
export type Agent = { id:number; species:Species; x:number; y:number; angle:number; energy:number; age:number; cooldown:number; target:number|null; state:string; speed:number; burrowId?:number|null; shelterUntil?:number; shelterCooldown?:number };
export type Burrow = { id:number; x:number; y:number; capacity:number };
export type Plant = { x:number; y:number; growth:number };
export type Settings = { prey:number; predators:number; plants:number; regrowth:number; preySpeed:number; predatorSpeed:number; metabolism:number; burrows:number; burrowCapacity:number };
export type Sample = { time:number; prey:number; predators:number; plants:number; sheltered:number };
export const defaults:Settings = { prey:65,predators:9,plants:260,regrowth:1,preySpeed:36,predatorSpeed:47,metabolism:1,burrows:6,burrowCapacity:5 };
export const WIDTH=1200, HEIGHT=800, STEP=1/30, MAX_AGENTS=650;
export class Simulation {
  burrows:Burrow[]=[]; agents:Agent[]=[]; plants:Plant[]=[]; history:Sample[]=[]; time=0; births=0; deaths=0; eaten=0; seed:number; private nextId=1; private lastSample=-1;
  constructor(public settings:Settings={...defaults}, seed=42){ this.seed=seed>>>0; for(let i=0;i<settings.plants;i++)this.plants.push({x:24+this.random()*(WIDTH-48),y:24+this.random()*(HEIGHT-48),growth:this.random()}); for(let i=0;i<settings.burrows;i++)this.burrows.push({id:i+1,x:130+(i%3)*440,y:130+Math.floor(i/3)*540/Math.max(1,Math.ceil(settings.burrows/3)-1),capacity:settings.burrowCapacity}); this.add('prey',settings.prey); this.add('predator',settings.predators); this.sample(); }
  random(){ this.seed=(Math.imul(1664525,this.seed)+1013904223)>>>0; return this.seed/4294967296; }
  add(species:Species,count=1,x?:number,y?:number){ for(let i=0;i<count&&this.agents.length<MAX_AGENTS;i++)this.agents.push({id:this.nextId++,species,x:x??40+this.random()*(WIDTH-80),y:y??40+this.random()*(HEIGHT-80),angle:this.random()*Math.PI*2,energy:species==='prey'?72:100,age:0,cooldown:8+this.random()*12,target:null,state:'Explore',speed:.9+this.random()*.2}); }
  occupancy(id:number){return this.agents.filter(a=>a.burrowId===id&&a.energy>0).length;}
  setCapacity(id:number,capacity:number){const b=this.burrows.find(b=>b.id===id);if(b)b.capacity=Math.max(this.occupancy(id),Math.min(30,Math.max(0,Math.floor(capacity))));}
  tick(dt=STEP){
    this.time+=dt;
    for(const p of this.plants)p.growth=Math.min(1,p.growth+dt*.045*this.settings.regrowth);
    const dead=new Set<number>(); const children:{species:Species;x:number;y:number}[]=[];
    // Decisions use a snapshot. Deaths and births are committed after the tick.
    const alive=this.agents.filter(a=>a.energy>0);
    for(const a of alive){
      if(dead.has(a.id))continue;
      const previousTarget=a.target;
      a.age+=dt; a.cooldown-=dt; a.target=null;
      if(a.burrowId!=null){
        a.energy-=dt*2.9*this.settings.metabolism;
        if(a.energy<=0||a.age>210){dead.add(a.id);continue;}
        const home=this.burrows.find(b=>b.id===a.burrowId);
        const danger=home&&alive.some(b=>b.species==='predator'&&Math.hypot(b.x-home.x,b.y-home.y)<150);
        if(home&&a.energy>45&&(this.time<(a.shelterUntil??0)||danger)){a.state='À l’abri';continue;}
        a.burrowId=null;a.shelterCooldown=this.time+8;
        // Leave on the side opposite the nearest predator.
        const nearest=home?alive.filter(b=>b.species==='predator').sort((b,c)=>Math.hypot(b.x-home.x,b.y-home.y)-Math.hypot(c.x-home.x,c.y-home.y))[0]:undefined;
        if(home){a.angle=nearest?Math.atan2(home.y-nearest.y,home.x-nearest.x):a.angle;a.x=Math.max(18,Math.min(WIDTH-18,home.x+Math.cos(a.angle)*22));a.y=Math.max(18,Math.min(HEIGHT-18,home.y+Math.sin(a.angle)*22));}
        a.state='Cherche à manger';continue;
      }
      let tx=a.x+Math.cos(a.angle)*35,ty=a.y+Math.sin(a.angle)*35,mult=1;
      if(a.species==='prey'){
        let threat=alive.find(b=>b.id===previousTarget&&b.species==='predator'&&!dead.has(b.id)&&(a.x-b.x)**2+(a.y-b.y)**2<145*145);
        let best=threat?((a.x-threat.x)**2+(a.y-threat.y)**2)*.64:125*125;
        for(const b of alive)if(b.species==='predator'&&!dead.has(b.id)){const d=(a.x-b.x)**2+(a.y-b.y)**2;if(d<best){best=d;threat=b;}}
        if(threat){
          const refuge=a.energy>45&&this.time>=(a.shelterCooldown??0)?this.burrows.filter(b=>this.occupancy(b.id)<b.capacity&&Math.hypot(b.x-a.x,b.y-a.y)<240).sort((b,c)=>Math.hypot(b.x-a.x,b.y-a.y)-Math.hypot(c.x-a.x,c.y-a.y))[0]:undefined;
          mult=1.27;a.target=threat.id;
          if(refuge){tx=refuge.x;ty=refuge.y;a.state='Rejoint un terrier';if(Math.hypot(tx-a.x,ty-a.y)<16){a.burrowId=refuge.id;a.shelterUntil=this.time+4;a.x=refuge.x;a.y=refuge.y;a.state='À l’abri';a.energy-=dt*2.9*this.settings.metabolism;continue;}}
          else{tx=a.x+(a.x-threat.x)*3;ty=a.y+(a.y-threat.y)*3;a.state='Fuit';}
        }
        else {let food:Plant|undefined,dist=160*160;for(const p of this.plants)if(p.growth>=.75){const d=(a.x-p.x)**2+(a.y-p.y)**2;if(d<dist){dist=d;food=p;}}if(food){tx=food.x;ty=food.y;a.state='Broute';if(dist<15*15&&food.growth>=.75){food.growth=0;a.energy+=24;}}else a.state='Explore';}
      }else{
        let victim:Agent|undefined,dist=205*205;
        for(const b of alive)if(b.species==='prey'&&b.burrowId==null&&!dead.has(b.id)){const d=(a.x-b.x)**2+(a.y-b.y)**2;if(d<dist){dist=d;victim=b;}}
        if(victim){tx=victim.x;ty=victim.y;a.target=victim.id;a.state='Chasse';if(dist<17*17){dead.add(victim.id);a.energy+=65;this.eaten++;}}
        else a.state='Explore';
      }
      if(a.state==='Explore')a.angle+=(this.random()-.5)*2.5*dt;
      else a.angle=Math.atan2(ty-a.y,tx-a.x);
      const speed=(a.species==='prey'?this.settings.preySpeed:this.settings.predatorSpeed)*a.speed*mult;
      a.x+=Math.cos(a.angle)*speed*dt;a.y+=Math.sin(a.angle)*speed*dt;
      if(a.x<18||a.x>WIDTH-18){a.angle=Math.PI-a.angle;a.x=Math.max(18,Math.min(WIDTH-18,a.x));}
      if(a.y<18||a.y>HEIGHT-18){a.angle=-a.angle;a.y=Math.max(18,Math.min(HEIGHT-18,a.y));}
      a.energy-=dt*(a.species==='prey'?2.9*mult:4.1)*this.settings.metabolism;
      if(a.energy<=0||a.age>(a.species==='prey'?210:260))dead.add(a.id);
      else if(a.energy>(a.species==='prey'?112:168)&&a.cooldown<=0&&this.agents.length+children.length<MAX_AGENTS){a.energy*=.56;a.cooldown=a.species==='prey'?15:25;children.push({species:a.species,x:Math.max(20,Math.min(WIDTH-20,a.x+12)),y:Math.max(20,Math.min(HEIGHT-20,a.y+12))});}
      a.energy=Math.min(a.energy,220);
    }
    this.deaths+=dead.size;this.agents=this.agents.filter(a=>!dead.has(a.id));
    for(const c of children){this.add(c.species,1,c.x,c.y);this.births++;}
    if(Math.floor(this.time)>this.lastSample)this.sample();
  }
  sample(){this.lastSample=Math.floor(this.time);this.history.push({time:this.time,prey:this.agents.filter(a=>a.species==='prey').length,predators:this.agents.filter(a=>a.species==='predator').length,plants:this.plants.filter(p=>p.growth>=.75).length,sheltered:this.agents.filter(a=>a.burrowId!=null).length});if(this.history.length>3600)this.history.shift();}
}
