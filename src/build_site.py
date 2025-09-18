import os, json, hashlib, time
from pathlib import Path

import pandas as pd
from slugify import slugify
import qrcode
import yaml

# Validation (vérifie colonnes, doublons, valeurs hors bornes)
import src.validate_data as V

# ----- Chemins robustes (ancrés à la racine du repo) -------------------------
ROOT = Path(__file__).resolve().parents[1]   # /<repo>
DATA_DIR = ROOT / "data"
OUT = ROOT / "site_build"

# BASE_URL est injectée par GitHub Actions ; valeur par défaut pour usage local
REPO_URL_BASE = os.environ.get("BASE_URL", "https://<ton-user>.github.io/eco-score")

# ----- Utilitaires ------------------------------------------------------------
def ensure_dirs():
    (OUT / "p").mkdir(parents=True, exist_ok=True)
    (OUT / "qr").mkdir(parents=True, exist_ok=True)
    (OUT / "assets").mkdir(parents=True, exist_ok=True)

def write_style():
    css = """
html,body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,'Helvetica Neue',Arial,sans-serif;margin:0;padding:0}
main{max-width:880px;margin:24px auto;padding:0 16px}
table{width:100%;border-collapse:collapse}
th,td{padding:10px;border-bottom:1px solid #ddd}
.badge{padding:.2rem .5rem;border-radius:.35rem;display:inline-block;font-weight:700}
.badge.A{background:#e6ffed}
.badge.B{background:#f0f7ff}
.badge.C{background:#fff7e6}
.badge.D{background:#ffefe6}
.badge.E{background:#ffe6e6}
a{color:inherit}
header{padding:12px 16px;border-bottom:1px solid #eee}
input[type="search"]{padding:8px 12px;margin:12px 0;width:100%;max-width:360px;border:1px solid #ddd;border-radius:8px}
"""
    (OUT / "assets" / "style.css").write_text(css, encoding="utf-8")

def make_qr(url, dest):
    img = qrcode.make(url)
    img.save(dest)

def file_hash(path: Path) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]

def clamp01(x): return max(0.0, min(1.0, x))

def normalize(value, vmin, vmax):
    if vmax <= vmin:
        return 0.0
    return clamp01((value - vmin) / (vmax - vmin))

def auto_bounds(series: pd.Series, low=0.05, high=0.95):
    q = series.quantile([low, high]).values
    return float(q[0]), float(q[1])

def load_config():
    with open(ROOT / "config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def score_row(row, weights, bounds, grade_bands):
    e = normalize(row["base_kgco2e"], *bounds["base_kgco2e"])
    d = normalize(row["distance_km"], *bounds["distance_km"])
    b = normalize(row["biodiversity_risk"], *bounds["biodiversity_risk"])
    impact = weights["emissions"]*e + weights["distance"]*d + weights["biodiversity"]*b
    score100 = round(100*(1 - impact), 1)
    grade = next(g for g, cut in grade_bands if score100 >= cut)
    return score100, grade

# ----- Templates HTML ---------------------------------------------------------
def product_page_html(item, meta):
    return f"""<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{item['name']} — Éco-score</title>
<meta name="description" content="Fiche éco-score pour {item['name']}">
<link rel="stylesheet" href="{REPO_URL_BASE}/assets/style.css">
</head><body>
<header><a href="{REPO_URL_BASE}/">← Retour</a></header>
<main>
  <h1>{item['name']}</h1>
  <p><strong>Note :</strong> <span class="badge {item['grade']}">{item['grade']}</span> ({item['score']}/100)</p>
  <ul>
    <li>Émissions (unité produit) : {item['base_kgco2e']} kgCO₂e</li>
    <li>Distance estimée : {item['distance_km']} km</li>
    <li>Risque biodiversité : {item['biodiversity_risk']}</li>
  </ul>
  <h2>QR code</h2>
  <p>Scannez pour ouvrir cette fiche :</p>
  <img alt="QR code fiche {item['name']}" src="{REPO_URL_BASE}/qr/{item['slug']}.png" width="180">
  <h3>Sources & version</h3>
  <ul>
    <li>Agribalyse : {meta['data_source']['agribalyse']}</li>
    <li>Distances : {meta['data_source']['distances']}</li>
    <li>Biodiversité : {meta['data_source']['biodiversity']}</li>
    <li>Version de la méthode : {meta['method_version']}</li>
    <li>Build : {meta['build_time']}</li>
  </ul>
</main>
</body></html>"""

def index_html(items):
    rows = "\n".join(
        f"""<tr>
<td><a href="{REPO_URL_BASE}/p/{it['slug']}/">{it['name']}</a></td>
<td class="grade"><span class="badge {it['grade']}">{it['grade']}</span></td>
<td>{it['score']}</td>
</tr>"""
        for it in items
    )
    # Doubles accolades pour échapper le JS dans une f-string
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

# ----- Main build -------------------------------------------------------------
def main():
    ensure_dirs()
    write_style()

    # 1) Validation des données (raise explicite si problème)
    p, a, d, b = V.load_all()

    # 2) Config (poids, bornes, bandes, méta)
    cfg = load_config()
    weights = cfg["weights"]
    grade_bands = cfg["grade_bands"]
    bounds = cfg["bounds"]

    # 3) Fusion
    df = (p.merge(a, on="id", how="left")
            .merge(d, on="id", how="left")
            .merge(b, on="id", how="left"))
    df = df.rename(columns={"kgco2e_unit": "base_kgco2e"})

    # 4) Bornes automatiques si manquantes (percentiles 5–95)
    for key in ["base_kgco2e", "distance_km", "biodiversity_risk"]:
        v = bounds.get(key, None)
        if (not v) or (v[0] is None) or (v[1] is None):
            bounds[key] = list(auto_bounds(df[key].astype(float)))

    # 5) Génération pages + QR + manifest
    records = []
    for _, r in df.iterrows():
        slug = slugify(f"{r['id']}-{r['name']}")
        score100, grade = score_row(r, weights, bounds, grade_bands)
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
        meta = cfg["meta"] | {"build_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        (dest_dir / "index.html").write_text(product_page_html(rec, meta), encoding="utf-8")
        make_qr(url, OUT / "qr" / f"{slug}.png")

    manifest = {
        "records": records,
        "meta": {
            "build_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "method_version": cfg["meta"]["method_version"],
            "data_hash": {
                str(pth): file_hash(ROOT / pth) for pth in [
                    "data/products.csv", "data/agribalyse.csv", "data/distances.csv", "data/biodiv.csv"
                ]
            },
            "bounds": bounds,
            "weights": weights
        }
    }

    (OUT / "index.html").write_text(index_html(records), encoding="utf-8")
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
