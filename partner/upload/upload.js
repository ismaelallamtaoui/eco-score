import { parseCSV } from '../../../src/utils/csv.js';

const input = document.getElementById('file');
const out = document.getElementById('out');
document.getElementById('process').addEventListener('click', async ()=>{
  const f = input.files?.[0];
  if(!f){ out.textContent = 'Veuillez choisir un fichier CSV.'; return; }
  const txt = await f.text();
  const rows = parseCSV(txt);
  // very light validation
  const required = ['gtin','name','category','unit','originCountry','supplierId','lcaRefId'];
  const missingCols = required.filter(k=> !(k in rows[0] || rows.some(r=> k in r)));
  if(missingCols.length){ out.textContent = 'Colonnes manquantes: ' + missingCols.join(', '); return; }
  out.textContent = JSON.stringify(rows.slice(0,50), null, 2);
});
