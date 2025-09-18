import { defaultWeights } from './weights.js';
import { seasonFactor } from './season.js';
import { parseCSV } from '../utils/csv.js';

// Normalization helpers
function minmaxNorm(x, min, max){
  if(max===min) return 50;
  const v = (x - min) / (max - min);
  const bounded = Math.min(1, Math.max(0, 1 - v)); // lower raw impact = better score
  return Math.round(bounded * 100);
}

export async function loadCSV(path){
  const txt = await (await fetch(path, {cache:'no-store'})).text();
  return parseCSV(txt);
}

// Compute per product score and breakdown
export async function computeScore(product, ctx){
  // ctx: { lcaByRef, seasonTable, month (1-12), transportsByGtin, suppliersById }
  const weights = defaultWeights();
  const lca = ctx.lcaByRef[product.lcaRefId];
  if(!lca){ return { score: 0, letter: 'E', breakdown: [], note: 'No LCA' }; }

  // Raw impacts per unit
  let ghg = Number(lca.impacts.ghg || 0);
  let water = Number(lca.impacts.water || 0);
  let land = Number(lca.impacts.land || 0);
  let pm = Number(lca.impacts.pm || 0);
  let eutro = Number(lca.impacts.eutro || 0);
  let biodiversity = Number(lca.impacts.biodiversity || 0);
  if(!isFinite(biodiversity)) biodiversity = land * 0.2; // simple proxy if missing

  // Transport addition (kgCO2e) from data/transport.csv if present
  const tlegs = (ctx.transportsByGtin[product.gtin] || []);
  const tAdd = tlegs.reduce((acc, leg)=> acc + Number(leg.km || 0) * Number(leg.emissionFactor || 0), 0);
  ghg += tAdd;

  // Seasonality adjustment (only applied to GHG here, could apply to others)
  const sf = seasonFactor(product.category || '', ctx.month || (new Date().getMonth()+1), ctx.seasonTable || []);
  ghg = ghg / (sf || 1);

  // Simple per-category normalization using contextual percentiles (demo: fixed brackets)
  const CAT = (product.category || 'General').toLowerCase();
  const norms = ctx.norms[CAT] || ctx.norms['default'];
  const n = {
    ghg: minmaxNorm(ghg, norms.ghg.min, norms.ghg.max),
    water: minmaxNorm(water, norms.water.min, norms.water.max),
    land: minmaxNorm(land, norms.land.min, norms.land.max),
    biodiversity: minmaxNorm(biodiversity, norms.biodiversity.min, norms.biodiversity.max),
    pm: minmaxNorm(pm, norms.pm.min, norms.pm.max),
    eutro: minmaxNorm(eutro, norms.eutro.min, norms.eutro.max)
  };

  // Socio-ethics small bonus/malus from supplier certs/practices
  let adj = 0;
  const sup = ctx.suppliersById[product.supplierId];
  if(sup){
    const certs = (sup.certs||'').toUpperCase();
    if(certs.includes('AB') or certs.includes('BIO')) adj += 3;
    if(certs.includes('FAIR') or certs.includes('EQ')) adj += 2;
    if((sup.practices||'').toLowerCase().includes('agroecology')) adj += 2;
  }

  const contributions = [
    ['ghg','Climat'],
    ['water','Eau'],
    ['land','Sols'],
    ['biodiversity','Biodiversité'],
    ['pm','Particules'],
    ['eutro','Eutrophisation']
  ].map(([k,label])=> ({
    key:k, label, normalized:n[k], weight: Number(weights[k]||0), contribution: Math.round(n[k]*Number(weights[k]||0))
  }));

  let score = contributions.reduce((a,c)=> a + c.contribution, 0) + adj;
  score = Math.max(0, Math.min(100, Math.round(score)));
  const letter = score>=90?'A':score>=75?'B':score>=60?'C':score>=45?'D':'E';

  return { score, letter, breakdown: contributions, adj, sf };
}

// Basic norms (demo values). In production compute from dataset percentiles.
export const defaultNorms = {
  "default": { "ghg": {"min":0.2,"max":15}, "water":{"min":5,"max":4000}, "land":{"min":0.1,"max":20}, "biodiversity":{"min":0.05,"max":5}, "pm":{"min":0.01,"max":0.5}, "eutro":{"min":0.01,"max":0.5} },
  "dairy": { "ghg": {"min":0.2,"max":5}, "water":{"min":5,"max":2000}, "land":{"min":0.05,"max":10}, "biodiversity":{"min":0.02,"max":3}, "pm":{"min":0.005,"max":0.2}, "eutro":{"min":0.005,"max":0.3} }
};
