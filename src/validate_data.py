from pathlib import Path
import pandas as pd

# Ancre les chemins à la racine du repo, peu importe d'où Python est lancé
ROOT = Path(__file__).resolve().parents[1]        # /<repo>
DATA_DIR = ROOT / "data"

REQUIRED = {
    "products": ["id", "name"],
    "agribalyse": ["id", "kgco2e_unit"],
    "distances": ["id", "distance_km"],
    "biodiv": ["id", "biodiversity_risk"],
}

def ensure_cols(df, cols, name):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{name}: colonnes manquantes {missing}")

def load_all():
    # Lis les CSV avec des chemins absolus
    p = pd.read_csv(DATA_DIR / "products.csv")
    a = pd.read_csv(DATA_DIR / "agribalyse.csv")
    d = pd.read_csv(DATA_DIR / "distances.csv")
    b = pd.read_csv(DATA_DIR / "biodiv.csv")

    ensure_cols(p, REQUIRED["products"], "products")
    ensure_cols(a, REQUIRED["agribalyse"], "agribalyse")
    ensure_cols(d, REQUIRED["distances"], "distances")
    ensure_cols(b, REQUIRED["biodiv"], "biodiv")

    # IDs dupliqués ?
    for df, name in [(a,"agribalyse"), (d,"distances"), (b,"biodiv"), (p,"products")]:
        if df["id"].duplicated().any():
            dups = df[df["id"].duplicated()]["id"].tolist()
            raise ValueError(f"{name}: IDs dupliqués {dups}")

    # Valeurs hors bornes
    if (a["kgco2e_unit"] < 0).any():
        raise ValueError("agribalyse: kgco2e_unit négatif détecté")
    if (d["distance_km"] < 0).any():
        raise ValueError("distances: distance_km négatif détecté")
    if ((b["biodiversity_risk"] < 0) | (b["biodiversity_risk"] > 1)).any():
        raise ValueError("biodiv: biodiversity_risk doit être entre 0 et 1")

    return p, a, d, b
