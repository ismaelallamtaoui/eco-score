import { defaultWeights, saveWeights } from '../src/score/weights.js';
import { computeScore, defaultNorms, loadCSV } from '../src/score/compute.js';

const tbody = document.querySelector('#productsTable tbody');
const loadBtn = document.getElementById('loadDemo');
const clearBtn = document.getElementById('clear');
const slidersDiv = document.getElementById('sliders');

let ctx = {
  lcaByRef: {},
  seasonTable: [],
  transportsByGtin: {},
  suppliersById: {},
  month: (new Date().getMonth()+1),
  norms: defaultNorms
};

async function init(){
  // Load auxiliary data
  const [lca, season, trans, sups] = await Promise.all([
    loadCSV('../data/examples/lca.csv'),
    loadCSV('../data/seasonality.csv'),
    loadCSV('../data/examples/transport.csv'),
    loadCSV('../data/suppliers.csv')
  ]);
  lca.forEach(r=> ctx.lcaByRef[r.ref] = { impacts: {
    ghg: Number(r.ghg), water: Number(r.water), land: Number(r.land), pm: Number(r.pm), eutro: Number(r.eutro), biodiversity: Number(r.biodiversity||NaN)
  }});
  ctx.seasonTable = season;
  trans.forEach(r=> {
    ctx.transportsByGtin[r.gtin] = ctx.transportsByGtin[r.gtin] || [];
    ctx.transportsByGtin[r.gtin].push({mode:r.mode, km:Number(r.km), emissionFactor:Number(r.emissionFactor)});
  });
  sups.forEach(s=> ctx.suppliersById[s.id] = s);

  renderSliders();
}
init();

function renderSliders(){
  const w = defaultWeights();
  slidersDiv.innerHTML = '';
  for(const k of ['ghg','water','land','biodiversity','pm','eutro']){
    const wrap = document.createElement('div');
    wrap.className = 'slider';
    wrap.innerHTML = `<label>${k}</label>
      <input type="range" min="0" max="100" step="5" value="${Math.round((w[k]||0)*100)}">
      <span class="val">${Math.round((w[k]||0)*100)}%</span>`;
    const input = wrap.querySelector('input');
    const span = wrap.querySelector('.val');
    input.addEventListener('input', ()=> { span.textContent = input.value + '%'; });
    input.addEventListener('change', ()=> {
      // renormalize to sum = 100
      const sliders = Array.from(slidersDiv.querySelectorAll('input'));
      const raw = sliders.map(s=> Number(s.value));
      const sum = raw.reduce((a,b)=>a+b,0) || 1;
      const keys = ['ghg','water','land','biodiversity','pm','eutro'];
      const out = {};
      sliders.forEach((s,i)=> out[keys[i]] = (raw[i]/sum));
      saveWeights(out);
      if(window.productsCache) renderTable(window.productsCache); // update scores
    });
    slidersDiv.appendChild(wrap);
  }
}

loadBtn.addEventListener('click', async ()=>{
  const products = await loadCSV('../data/products.csv');
  window.productsCache = products;
  renderTable(products);
});

clearBtn.addEventListener('click', ()=>{
  tbody.innerHTML='';
  window.productsCache = null;
});

async function renderTable(products){
  tbody.innerHTML = '';
  for(const p of products){
    const res = await computeScore(p, ctx);
    const tr = document.createElement('tr');
    tr.innerHTML = \`
      <td>\${p.gtin}</td>
      <td>\${p.name}</td>
      <td>\${p.originCountry}</td>
      <td><b>\${res.score}</b></td>
      <td class="badge badge-\${res.letter}">\${res.letter}</td>
      <td>
        <a href="../p/?gtin=\${encodeURIComponent(p.gtin)}">Fiche</a> ·
        <button data-gtin="\${p.gtin}" class="add">+ Panier</button>
      </td>\`;
    tbody.appendChild(tr);
  }
  tbody.querySelectorAll('button.add').forEach(btn=> btn.addEventListener('click', ()=> addToBasket(btn.dataset.gtin)));
}

function addToBasket(gtin){
  const basket = JSON.parse(localStorage.getItem('meta_basket_v1') || '{}');
  basket[gtin] = (basket[gtin]||0) + 1;
  localStorage.setItem('meta_basket_v1', JSON.stringify(basket));
  alert('Ajouté au panier');
}
