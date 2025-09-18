from pathlib import Path
import json, csv

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "site_build"
OUT_DIR = ROOT / "artifacts"
OUT_DIR.mkdir(exist_ok=True, parents=True)

def main():
    manifest = json.loads((BUILD / "manifest.json").read_text(encoding="utf-8"))
    rows = manifest["records"]
    out = OUT_DIR / "scores.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id","name","grade","score","base_kgco2e","distance_km","biodiversity_risk","url"])
        for r in rows:
            w.writerow([r["id"], r["name"], r["grade"], r["score"], r["base_kgco2e"], r["distance_km"], r["biodiversity_risk"], r["url"]])
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
