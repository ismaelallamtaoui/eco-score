import { computeScore, defaultNorms, loadCSV } from '../src/score/compute.js';

const tbody = document.querySelector('#basketTable tbody');
const totalsDiv = document.getElementById('totals');
const hintsDiv = document.getElementById('suggestions');

let ctx = {
  lcaByRef: {},
  seasonTable: [],
  transportsByGtin: {},
  suppliersById: {},
  month: (new Date().getMonth()+1),
  norms: defaultNorms
};

async function init(){
  const [products, lca, season, trans, sups] = await Promise.all([
    loadCSV('../data/products.csv'),
    loadCSV('../data/examples/lca.csv'),
    loadCSV('../data/seasonality.csv'),
    loadCSV('../data/examples/transport.csv'),
    loadCSV('../data/suppliers.csv')
  ]);
  const byGtin = {}; products.forEach(p=> byGtin[p.gtin]=p);
  lca.forEach(r=> ctx.lcaByRef[r.ref] = { impacts: {
    ghg: Number(r.ghg), water: Number(r.water), land: Number(r.land), pm: Number(r.pm), eutro: Number(r.eutro), biodiversity: Number(r.biodiversity||NaN)
  }});
  ctx.seasonTable = season;
  trans.forEach(r=> {
    ctx.transportsByGtin[r.gtin] = ctx.transportsByGtin[r.gtin] || [];
    ctx.transportsByGtin[r.gtin].push({mode:r.mode, km:Number(r.km), emissionFactor:Number(r.emissionFactor)});
  });
  sups.forEach(s=> ctx.suppliersById[s.id] = s);

  const basket = JSON.parse(localStorage.getItem('meta_basket_v1')||'{}');
  let totCO2 = 0, totWater = 0, totScore = 0, n=0;

  tbody.innerHTML='';
  for(const [gtin, qty] of Object.entries(basket)){
    const p = byGtin[gtin];
    if(!p) continue;
    const res = await computeScore(p, ctx);
    const l = ctx.lcaByRef[p.lcaRefId];
    const rowCO2 = (l.impacts.ghg||0) * qty;
    const rowWater = (l.impacts.water||0) * qty;
    totCO2 += rowCO2; totWater += rowWater; totScore += res.score; n++;

    const tr = document.createElement('tr');
    tr.innerHTML = \`<td>\${gtin}</td><td>\${p.name}</td>
      <td>\${qty}</td><td>\${rowCO2.toFixed(2)}</td><td>\${rowWater.toFixed(0)}</td><td>\${res.letter} (\${res.score})</td>\`;
    tbody.appendChild(tr);
  }

  totalsDiv.textContent = \`\${totCO2.toFixed(1)} kgCO₂e — \${totWater.toFixed(0)} L d'eau — Score moyen \${n?Math.round(totScore/n):0}\`;
  // naive suggestion: if beef present, suggest lentils (demo)
  const hasBeef = Object.keys(JSON.parse(localStorage.getItem('meta_basket_v1')||'{}')).some(gtin=> (byGtin[gtin]?.category||'').toLowerCase().includes('beef'));
  if(hasBeef){
    hintsDiv.textContent = "Suggestion : remplacer un produit 'beef' par 'lentils' peut réduire le CO₂ de ~80% (démonstration).";
  } else {
    hintsDiv.textContent = "";
  }
}
init();
