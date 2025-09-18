import { computeScore, defaultNorms, loadCSV } from '../src/score/compute.js';

const container = document.getElementById('product');

function params(){ const q=new URLSearchParams(location.search); return Object.fromEntries(q.entries()); }

async function init(){
  const gtin = params().gtin;
  if(!gtin){ container.textContent = 'GTIN manquant'; return; }

  const [products, lca, season, trans, sups] = await Promise.all([
    loadCSV('../data/products.csv'),
    loadCSV('../data/examples/lca.csv'),
    loadCSV('../data/seasonality.csv'),
    loadCSV('../data/examples/transport.csv'),
    loadCSV('../data/suppliers.csv')
  ]);
  const p = products.find(r=> r.gtin===gtin);
  if(!p){ container.textContent = 'Produit introuvable'; return; }

  const ctx = { lcaByRef:{}, seasonTable: season, transportsByGtin:{}, suppliersById:{}, month:(new Date().getMonth()+1), norms: defaultNorms };
  lca.forEach(r=> ctx.lcaByRef[r.ref] = { impacts: {
    ghg: Number(r.ghg), water: Number(r.water), land: Number(r.land), pm: Number(r.pm), eutro: Number(r.eutro), biodiversity: Number(r.biodiversity||NaN)
  }});
  trans.forEach(r=> {
    ctx.transportsByGtin[r.gtin] = ctx.transportsByGtin[r.gtin] || [];
    ctx.transportsByGtin[r.gtin].push({mode:r.mode, km:Number(r.km), emissionFactor:Number(r.emissionFactor)});
  });
  sups.forEach(s=> ctx.suppliersById[s.id] = s);

  const res = await computeScore(p, ctx);

  container.innerHTML = `
    <div class="product">
      <h2>${p.name}</h2>
      <p><b>GTIN:</b> ${p.gtin} — <b>Origine:</b> ${p.originCountry} — <b>Catégorie:</b> ${p.category}</p>
      <p><span class="badge badge-${res.letter}">${res.letter}</span> Score ${res.score}</p>
      <h3>Détails</h3>
      <ul>
        ${res.breakdown.map(b=> `<li>${b.label}: ${b.normalized} (poids ${Math.round(b.weight*100)}%) → contrib ${b.contribution}</li>`).join('')}
      </ul>
      <p>Saisonnalité (facteur): ${res.sf}</p>
      <p><a href="../compare/">← Retour</a></p>
    </div>
  `;
}
init();
