import os, json
from pathlib import Path
import pandas as pd
from slugify import slugify
import qrcode

# BASE_URL is set automatically by GitHub Actions, or you can override locally
REPO_URL_BASE = os.environ.get("BASE_URL", "https://<ton-user>.github.io/eco-score-site")

WEIGHTS = {"emissions": 0.6, "distance": 0.2, "biodiversity": 0.2}
BOUNDS = {
    "base_kgco2e": (0.0, 10.0),
    "distance_km": (0.0, 3000.0),
    "biodiversity_risk": (0.0, 1.0)
}
GRADE_BANDS = [("A", 80), ("B", 60), ("C", 40), ("D", 20), ("E", 0)]

SRC = Path(".")
DATA = SRC / "data" / "products.csv"
OUT = SRC / "site_build"

def clamp01(x): return max(0.0, min(1.0, x))

def normalize(value, vmin, vmax):
    if vmax <= vmin: return 0.0
    return clamp01((value - vmin) / (vmax - vmin))

def score_row(row):
    e = normalize(row["base_kgco2e"], *BOUNDS["base_kgco2e"])
    d = normalize(row["distance_km"], *BOUNDS["distance_km"])
    b = normalize(row["biodiversity_risk"], *BOUNDS["biodiversity_risk"])
    impact = WEIGHTS["emissions"]*e + WEIGHTS["distance"]*d + WEIGHTS["biodiversity"]*b
    score100 = round(100*(1 - impact), 1)
    grade = next(g for g, cut in GRADE_BANDS if score100 >= cut)
    return score100, grade

def ensure_dirs():
    (OUT / "p").mkdir(parents=True, exist_ok=True)
    (OUT / "qr").mkdir(parents=True, exist_ok=True)
    (OUT / "assets").mkdir(parents=True, exist_ok=True)

def make_qr(url, dest):
    img = qrcode.make(url)
    img.save(dest)

def product_page_html(item):
    return f"""<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{item['name']} — Éco-score</title>
<link rel="stylesheet" href="{REPO_URL_BASE}/assets/style.css">
</head><body>
<header><a href="{REPO_URL_BASE}/">← Retour</a></header>
<main>
  <h1>{item['name']}</h1>
  <p><strong>Note :</strong> {item['grade']} ({item['score']}/100)</p>
  <ul>
    <li>Émissions (unité produit) : {item['base_kgco2e']} kgCO₂e</li>
    <li>Distance estimée : {item['distance_km']} km</li>
    <li>Risque biodiversité : {item['biodiversity_risk']}</li>
  </ul>
  <h2>QR code</h2>
  <p>Scannez pour ouvrir cette fiche :</p>
  <img alt="QR code" src="{REPO_URL_BASE}/qr/{item['slug']}.png" width="180">
</main>
<footer><p>© {item.get('year','2025')} — Éco-score déployé via GitHub Pages</p></footer>
</body></html>"""

def index_html(items):
    rows = "\n".join(
        f"""<tr>
<td><a href="{REPO_URL_BASE}/p/{it['slug']}/">{it['name']}</a></td>
<td class="grade">{it['grade']}</td>
<td>{it['score']}</td>
</tr>"""
        for it in items
    )
    return f"""<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Éco-score — Catalogue</title>
<link rel="stylesheet" href="{REPO_URL_BASE}/assets/style.css">
</head><body>
<main>
  <h1>Catalogue Éco-score</h1>
  <table>
    <thead><tr><th>Produit</th><th>Note</th><th>Score</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</main>
</body></html>"""

def write_style():
    css = """
html,body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,'Helvetica Neue',Arial,sans-serif;margin:0;padding:0}
main{max-width:880px;margin:24px auto;padding:0 16px}
table{width:100%;border-collapse:collapse}
th,td{padding:10px;border-bottom:1px solid #ddd}
.grade{font-weight:700}
a{color:inherit}
header{padding:12px 16px;border-bottom:1px solid #eee}
"""
    (OUT / "assets" / "style.css").write_text(css, encoding="utf-8")

def main():
    ensure_dirs()
    write_style()

    df = pd.read_csv(DATA)
    records = []
    for _, r in df.iterrows():
        slug = slugify(f"{r['id']}-{r['name']}")
        score100, grade = score_row(r)
        url = f"{REPO_URL_BASE}/p/{slug}/"
        rec = {
            "id": r["id"],
            "name": r["name"],
            "slug": slug,
            "url": url,
            "score": score100,
            "grade": grade,
            "base_kgco2e": float(r["base_kgco2e"]),
            "distance_km": float(r["distance_km"]),
            "biodiversity_risk": float(r["biodiversity_risk"]),
            "year": 2025
        }
        records.append(rec)

        dest_dir = OUT / "p" / slug
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "index.html").write_text(product_page_html(rec), encoding="utf-8")

        make_qr(url, OUT / "qr" / f"{slug}.png")

    (OUT / "index.html").write_text(index_html(records), encoding="utf-8")
    (OUT / "manifest.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
