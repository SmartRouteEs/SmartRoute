import pickle
import json
from pathlib import Path
import numpy as np
from scipy.spatial import KDTree

GRAPH_FILE = "data/processed/graph_with_strava_and_dplus.gpickle"
MATCHED_JSON = Path("data/matched_traces") / "allee-de-maintenon_cleaned_matched.json"

def extract_shape_points(data):
    legs = data.get("trip", {}).get("legs", [])
    all_points = []
    for leg in legs:
        shape_raw = leg.get("shape")
        if not shape_raw:
            continue
        if isinstance(shape_raw, str):
            import polyline
            decoded = polyline.decode(shape_raw)
            all_points.extend(decoded)
        elif isinstance(shape_raw, list):
            all_points.extend(shape_raw)
    return all_points

# Charger graphe
with open(GRAPH_FILE, "rb") as fg:
    G = pickle.load(fg)

# Charger la trace matched
with open(MATCHED_JSON, "r") as f:
    valhalla_result = json.load(f)

shape_points = extract_shape_points(valhalla_result)

# --- Affiche les premiers points pour vérification
print("Premiers points de la polyline Valhalla :")
for pt in shape_points[:5]:
    print(pt)
print("\n")

# --- Affiche les premiers nœuds du graphe
node_ids = []
node_coords = []
for nid, data in G.nodes(data=True):
    lat = data.get("y")
    lon = data.get("x")
    if lat is not None and lon is not None:
        node_ids.append(nid)
        node_coords.append([lat, lon])
print("Premier nœud du graphe :")
print(node_ids[0], node_coords[0])
print("\n")

# --- Compare plage de valeurs
shape_lats = [pt[0] for pt in shape_points]
shape_lons = [pt[1] for pt in shape_points]
graph_lats = [c[0] for c in node_coords]
graph_lons = [c[1] for c in node_coords]
print(f"Latitude (Valhalla polyline) min/max: {min(shape_lats):.4f}/{max(shape_lats):.4f}")
print(f"Longitude (Valhalla polyline) min/max: {min(shape_lons):.4f}/{max(shape_lons):.4f}")
print(f"Latitude (graphe) min/max: {min(graph_lats):.4f}/{max(graph_lats):.4f}")
print(f"Longitude (graphe) min/max: {min(graph_lons):.4f}/{max(graph_lons):.4f}")

# --- Crée un KDTree et teste l'association sur 5 points
node_coords_arr = np.array(node_coords)
kdtree = KDTree(node_coords_arr)
print("\nAssociation Valhalla → nœud du graphe :")
for pt in shape_points[:5]:
    dist, idx = kdtree.query(pt)
    nid = node_ids[idx]
    print(f"  Point polyline {pt} ➔ nœud {nid} coord: {node_coords[idx]}, dist={dist:.2f} m")
