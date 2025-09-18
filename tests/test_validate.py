from pathlib import Path
import pandas as pd
import src.validate_data as V

def test_validate_columns(tmp_path, monkeypatch):
    # créer des csv temporaires valides
    d = tmp_path / "data"; d.mkdir()
    (d / "products.csv").write_text("id,name\na,b\n", encoding="utf-8")
    (d / "agribalyse.csv").write_text("id,kgco2e_unit\na,1\n", encoding="utf-8")
    (d / "distances.csv").write_text("id,distance_km\na,10\n", encoding="utf-8")
    (d / "biodiv.csv").write_text("id,biodiversity_risk\na,0.1\n", encoding="utf-8")
    # monkeypatch ROOT/DATA_DIR
    monkeypatch.setattr(V, "ROOT", tmp_path)
    monkeypatch.setattr(V, "DATA_DIR", d)
    p,a,di,b = V.load_all()
    assert list(p.columns) == ["id","name"]
