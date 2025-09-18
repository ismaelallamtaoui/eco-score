def index_html(items):
    rows = "\n".join(
        f"""<tr>
<td><a href="{REPO_URL_BASE}/p/{it['slug']}/">{it['name']}</a></td>
<td class="grade"><span class="badge {it['grade']}">{it['grade']}</span></td>
<td>{it['score']}</td>
</tr>"""
        for it in items
    )
    # NB: toutes les accolades { } du JS sont doublées {{ }}
    return f"""<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Éco-score — Catalogue</title>
<link rel="stylesheet" href="{REPO_URL_BASE}/assets/style.css">
</head><body>
<main>
  <h1>Catalogue Éco-score</h1>
  <input id="q" type="search" placeholder="Rechercher un produit...">
  <table>
    <thead><tr><th>Produit</th><th>Note</th><th>Score</th></tr></thead>
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
