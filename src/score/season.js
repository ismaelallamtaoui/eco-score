// Seasonality: returns factor in (0,1] (1 = in season)
export function seasonFactor(category, month, table){
  const rows = table.filter(r => r.category.toLowerCase() === category.toLowerCase() && Number(r.month) === month);
  if(rows.length === 0) return 1;
  const f = Number(rows[0].factor);
  if(!isFinite(f) || f <= 0) return 1;
  return Math.min(1, Math.max(0.1, f));
}
