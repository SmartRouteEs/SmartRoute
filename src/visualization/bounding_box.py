import pickle
from pathlib import Path

GRAPH_PATH = Path("data/processed/graph_with_strava_and_dplus.gpickle")

with open(GRAPH_PATH, "rb") as f:
    G = pickle.load(f)

xs = [data["x"] for _, data in G.nodes(data=True) if "x" in data]
ys = [data["y"] for _, data in G.nodes(data=True) if "y" in data]

lon_min, lon_max = min(xs), max(xs)
lat_min, lat_max = min(ys), max(ys)

print("🗺️ Bounding box du graphe enrichi :")
print(f" - Longitude : {lon_min:.6f} → {lon_max:.6f}")
print(f" - Latitude  : {lat_min:.6f} → {lat_max:.6f}")
