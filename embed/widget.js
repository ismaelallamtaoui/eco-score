// Simple embeddable widget (no framework)
export function initWidget({ el, gtin, theme='light' }){
  const root = (typeof el === 'string') ? document.querySelector(el) : el;
  if(!root) return;
  const url = new URL('/p/', location.origin);
  url.searchParams.set('gtin', gtin);
  root.innerHTML = \`
    <iframe src="\${url.toString()}" style="width:100%;height:220px;border:0;"></iframe>
  \`;
}
