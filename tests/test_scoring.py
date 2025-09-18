import types
import pandas as pd

# Minimal functions replicated for unit tests
def clamp01(x): return max(0.0, min(1.0, x))

def normalize(value, vmin, vmax):
    if vmax <= vmin:
        return 0.0
    return clamp01((value - vmin) / (vmax - vmin))

def score_row(row, weights, bounds, grade_bands):
    e = normalize(row["base_kgco2e"], *bounds["base_kgco2e"])
    d = normalize(row["distance_km"], *bounds["distance_km"])
    b = normalize(row["biodiversity_risk"], *bounds["biodiversity_risk"])
    impact = weights["emissions"]*e + weights["distance"]*d + weights["biodiversity"]*b
    score100 = round(100*(1 - impact), 1)
    grade = next(g for g, cut in grade_bands if score100 >= cut)
    return score100, grade

def test_normalize_bounds():
    assert normalize(5, 0, 10) == 0.5
    assert normalize(-5, 0, 10) == 0.0
    assert normalize(15, 0, 10) == 1.0
    assert normalize(1, 1, 1) == 0.0

def test_score_row_monotonic():
    weights = {"emissions":0.6, "distance":0.2, "biodiversity":0.2}
    bounds = {"base_kgco2e":(0,10), "distance_km":(0,3000), "biodiversity_risk":(0,1)}
    bands = [("A",80),("B",60),("C",40),("D",20),("E",0)]
    r1 = {"base_kgco2e":1, "distance_km":100, "biodiversity_risk":0.1}
    r2 = {"base_kgco2e":5, "distance_km":1000, "biodiversity_risk":0.5}
    s1,_ = score_row(r1, weights, bounds, bands)
    s2,_ = score_row(r2, weights, bounds, bands)
    assert s1 > s2  # plus “propre” -> score plus haut
