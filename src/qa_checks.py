from pathlib import Path
import pandas as pd
import yaml, sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CFG = ROOT / "qa_rules.yaml"

def fail(msg):
    print(f"QA FAIL: {msg}")
    sys.exit(1)

def main():
    cfg = yaml.safe_load(CFG.read_text(encoding="utf-8"))
    # charger tables
    try:
        products = pd.read_csv(DATA / "products.csv")
        agr = pd.read_csv(DATA / "agribalyse.csv")
        dist = pd.read_csv(DATA / "distances.csv")
        biod = pd.read_csv(DATA / "biodiv.csv")
    except FileNotFoundError as e:
        fail(str(e))

    # jointure minimale pour contrôles transverses
    df = (products.merge(agr, on="id", how="left")
                 .merge(dist, on="id", how="left")
                 .merge(biod, on="id", how="left"))

    # Renommage cohérent avec le build
    if "kgco2e_unit" in df.columns:
        df = df.rename(columns={"kgco2e_unit":"base_kgco2e"})

    # colonnes manquantes
    if cfg.get("no_missing_columns", False):
        required = ["id","name","base_kgco2e","distance_km","biodiversity_risk"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            fail(f"Colonnes manquantes: {missing}")

    # valeurs manquantes
    if df[["id","name","base_kgco2e","distance_km","biodiversity_risk"]].isna().any().any():
        bad = df[df[["base_kgco2e","distance_km","biodiversity_risk"]].isna().any(axis=1)]
        fail(f"Valeurs manquantes détectées sur {len(bad)} lignes (ex: {bad.head(3).to_dict(orient='records')})")

    # max
    for col, mx in (cfg.get("max_values") or {}).items():
        if col in df.columns and (df[col] > mx).any():
            top = df[df[col] > mx][["id","name",col]].head(5).to_dict(orient="records")
            fail(f"{col} > {mx} détecté (exemples: {top})")

    # ranges
    ranges = cfg.get("ranges") or {}
    for col, (mn, mx) in ranges.items():
        if col in df.columns and ((df[col] < mn) | (df[col] > mx)).any():
            bad = df[(df[col] < mn) | (df[col] > mx)][["id","name",col]].head(5).to_dict(orient="records")
            fail(f"{col} hors [{mn},{mx}] détecté (ex: {bad})")

    print("QA OK: règles respectées")

if __name__ == "__main__":
    main()
