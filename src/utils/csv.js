export function parseCSV(text){
  const lines = text.replace(/\r/g,'').split('\n').filter(Boolean);
  if(lines.length===0) return [];
  const headers = splitCSVLine(lines[0]);
  return lines.slice(1).map(line => {
    const cells = splitCSVLine(line);
    const obj = {};
    headers.forEach((h,i)=> obj[h] = cells[i]);
    return obj;
  });
}
function splitCSVLine(line){
  const res = [];
  let cur = '', inQ = false;
  for(let i=0;i<line.length;i++){
    const ch = line[i];
    if(ch==='"'){ inQ = !inQ; continue; }
    if(ch===',' && !inQ){ res.push(cur); cur=''; continue; }
    cur += ch;
  }
  res.push(cur);
  return res;
}
