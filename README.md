# Éco-score (Starter)

Ce dépôt génère un petit site statique sur GitHub Pages à partir d'un CSV (`data/products.csv`).
À chaque modification du CSV, GitHub Actions reconstruit le site et publie automatiquement.

## Utilisation rapide

1. Mettez vos produits dans `data/products.csv` (mêmes colonnes).
2. Commit/push sur la branche `main`.
3. Ouvrez l'onglet **Actions** → `build-and-deploy` doit passer au vert.
4. Le site sera disponible à l'URL : `https://<votre-user>.github.io/<nom-du-repo>/`.

Le script lit le CSV, calcule un score simple et génère :
- `site_build/index.html` (liste des produits),
- `site_build/p/<slug>/index.html` (pages produit),
- `site_build/qr/<slug>.png` (QR codes),
- `site_build/assets/style.css`,
- `site_build/manifest.json` (données pour un front JS si besoin).

## Local (optionnel)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.build_site
open site_build/index.html
```

> En CI, `BASE_URL` est défini automatiquement pour pointer vers votre Pages. En local, vous pouvez le définir :  
> `export BASE_URL="https://monuser.github.io/monrepo"`
