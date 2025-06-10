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


# Remplace par une trace de ton dossier gpx_clean
with open("data/gpx_clean/fontainebleau (12).pkl", "rb") as f:
    trace = pickle.load(f)

trace_lats = [pt[0] for pt in trace]
trace_lons = [pt[1] for pt in trace]

print("BBox de la trace :")
print(f"  Latitude  : {min(trace_lats):.6f} → {max(trace_lats):.6f}")
print(f"  Longitude : {min(trace_lons):.6f} → {max(trace_lons):.6f}")

from osmnx.distance import nearest_nodes

lat, lon = 48.40452, 2.67791  # un point de ta trace

node = nearest_nodes(G, lon, lat)
print(f"Nœud le plus proche : {node}")
print(G.nodes[node])


