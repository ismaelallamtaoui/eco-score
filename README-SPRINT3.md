# Sprint 3 — Gouvernance & Qualité

Ce pack ajoute :
- **QA automatique** (`src/qa_checks.py` + `qa_rules.yaml`) pour bloquer distances absurdes, notes incohérentes, valeurs manquantes.
- **Tests unitaires** (pytest) : normalisation, scoring, validation.
- **CI PR** (`.github/workflows/ci.yml`) : tests + QA sur chaque pull request.
- **Build renforcé** (`pages.yml`) : tests + QA avant build & déploiement.
- **Release** (`release.yml`) : créer une Release GitHub en poussant un tag `v*` et joindre `qr_sheets_a4.pdf` + `scores.csv`.
- **CODEOWNERS** : exige une revue pour `config.yaml`, `qa_rules.yaml`, `src/build_site.py`.
- **PR template** : checklist pour les contributeurs.
- **i18n** : `src/i18n_helpers.py` fournit un rendu d'index en anglais (tu peux l'appeler dans `build_site.py` pour générer `/en/index.html`).

## Intégration i18n (facultative)
Dans `src/build_site.py`, après avoir écrit `index.html`, tu peux :
```python
from src.i18n_helpers import index_html_en
(OUT / "en").mkdir(parents=True, exist_ok=True)
(OUT / "en" / "index.html").write_text(index_html_en(REPO_URL_BASE, records), encoding="utf-8")
```

## Lancer les tests en local
```
pip install -r requirements.txt
pip install pytest
pytest -q
python -m src.qa_checks
```
