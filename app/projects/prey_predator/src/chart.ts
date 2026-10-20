import type { Sample } from './engine';
export type Series = 'prey'|'predators'|'plants'|'sheltered';
export function chartWindow(history:Sample[],start:number,end:number){return history.filter(s=>s.time>=start&&s.time<=end);}
export function chartMaximum(data:Sample[],visible:Series[]){let max=10;for(const s of data)for(const key of visible)max=Math.max(max,s[key]);return max;}
