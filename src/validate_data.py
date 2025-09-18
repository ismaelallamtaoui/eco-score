import pandas as pd

REQUIRED = {
    "products": ["id","name"],
    "agribalyse": ["id","kgco2e_unit"],
    "distances": ["id","distance_km"],
    "biodiv": ["id","biodiversity_risk"],
}

def ensure_cols(df, cols, name):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{name}: colonnes manquantes {missing}")

def load_all():
    p = pd.read_csv("data/products.csv")
    a = pd.read_csv("data/agribalyse.csv")
    d = pd.read_csv("data/distances.csv")
    b = pd.read_csv("data/biodiv.csv")

    ensure_cols(p, REQUIRED["products"], "products")
    ensure_cols(a, REQUIRED["agribalyse"], "agribalyse")
    ensure_cols(d, REQUIRED["distances"], "distances")
    ensure_cols(b, REQUIRED["biodiv"], "biodiv")

    for df, name in [(a,"agribalyse"),(d,"distances"),(b,"biodiv"),(p,"products")]:
        if df["id"].duplicated().any():
            dups = df[df["id"].duplicated()]["id"].tolist()
            raise ValueError(f"{name}: IDs dupliqués {dups}")

    if (a["kgco2e_unit"] < 0).any():
        raise ValueError("agribalyse: kgco2e_unit négatif détecté")
    if (d["distance_km"] < 0).any():
        raise ValueError("distances: distance_km négatif détecté")
    if ((b["biodiversity_risk"] < 0) | (b["biodiversity_risk"] > 1)).any():
        raise ValueError("biodiv: biodiversity_risk doit être entre 0 et 1")

    return p,a,d,b
