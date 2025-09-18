def index_html_en(REPO_URL_BASE, items):
    rows = "\n".join(
        f"""<tr>
<td><a href="{REPO_URL_BASE}/p/{it['slug']}/">{it['name']}</a></td>
<td class="grade"><span class="badge {it['grade']}">{it['grade']}</span></td>
<td>{it['score']}</td>
</tr>"""
        for it in items
    )
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Eco-score — Catalog</title>
<link rel="stylesheet" href="{REPO_URL_BASE}/assets/style.css">
</head><body>
<main>
  <h1>Eco-score catalog</h1>
  <input id="q" type="search" placeholder="Search a product...">
  <table>
    <thead><tr><th>Product</th><th>Grade</th><th>Score</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</main>
<script>
const q = document.getElementById('q');
q.addEventListener('input', () => {{
  const term = q.value.toLowerCase();
  for (const tr of document.querySelectorAll('tbody tr')) {{
    tr.style.display = tr.innerText.toLowerCase().includes(term) ? '' : 'none';
  }}
}});
</script>
</body></html>"""
