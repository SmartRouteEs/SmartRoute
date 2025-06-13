import pickle
import json
from pathlib import Path
import numpy as np
from scipy.spatial import KDTree
import pandas as pd

GRAPH_PATH = "data/processed/graph_with_strava_and_dplus.gpickle"
MATCHED_DIR = Path("data/matched_traces")
OUT_DIR = Path("data/final_dataset")
OUT_DIR.mkdir(exist_ok=True)

with open(GRAPH_PATH, "rb") as fg:
    G = pickle.load(fg)
node_ids = []
node_coords = []
for nid, data in G.nodes(data=True):
    lat = data.get("y")
    lon = data.get("x")
    if lat is not None and lon is not None:
        node_ids.append(nid)
        node_coords.append([lat, lon])
node_coords = np.array(node_coords)
kdtree = KDTree(node_coords)

def find_nearest_node(coord):
    dist, idx = kdtree.query(coord)
    return node_ids[idx]

def extract_shape_points(data):
    points = []
    for leg in data.get("trip", {}).get("legs", []):
        shape_raw = leg.get("shape", "")
        if isinstance(shape_raw, str):
            import polyline
            decoded = polyline.decode(shape_raw)
            if any(abs(lat) > 90 or abs(lon) > 180 for lat, lon in decoded):
                decoded = [(lat / 10, lon / 10) for lat, lon in decoded]
            points.extend(decoded)
        elif isinstance(shape_raw, list):
            points.extend(shape_raw)
    return points

MAX_DIST = 0.002  # ~200 m, à ajuster selon la densité

rows = []

for json_file in MATCHED_DIR.glob("*_matched.json"):
    with open(json_file, "r") as f:
        data = json.load(f)
    shape_points = extract_shape_points(data)
    if not shape_points or len(shape_points) < 2:
        continue
    print(f"\n=== Trace : {json_file.name} ===")
    n_match, n_fail = 0, 0
    for i in range(len(shape_points) - 1):
        pt1, pt2 = shape_points[i], shape_points[i+1]
        u = find_nearest_node(pt1)
        v = find_nearest_node(pt2)
        if u == v:
            continue  # Ignore segments "à l'arrêt"
        lat1, lon1 = G.nodes[u]['y'], G.nodes[u]['x']
        lat2, lon2 = G.nodes[v]['y'], G.nodes[v]['x']
        dist = np.hypot(lat1 - lat2, lon1 - lon2)
        found = False
        # Cherche dans les deux sens (u,v) et (v,u)
        for dir_ in [(u, v), (v, u)]:
            if G.has_edge(*dir_) and dist < MAX_DIST:
                for k, edge_data in G[dir_[0]][dir_[1]].items():
                    if edge_data.get("dplus") is not None and edge_data.get("distance") is not None:
                        print(f"[MATCH] {dir_} k={k} : dplus={edge_data.get('dplus')}, distance={edge_data.get('distance')}, popularity={edge_data.get('popularity')}, surface={edge_data.get('surface')}")
                        rows.append({
                            "trace_file": json_file.name,
                            "edge_id": [int(dir_[0]), int(dir_[1]), int(k)],
                            "from_node": int(dir_[0]),
                            "to_node": int(dir_[1]),
                            "distance": float(edge_data.get("distance")),
                            "dplus": float(edge_data.get("dplus")),
                            "surface": str(edge_data.get("surface")),
                            "popularity": float(edge_data.get("popularity"))
                        })
                        n_match += 1
                        found = True
                        break
                if found:
                    break
        if not found:
            print(f"[FAIL] Pas de match enrichi pour ({u}, {v}) ou trop loin (Δlat={abs(lat1-lat2):.5f}, Δlon={abs(lon1-lon2):.5f}, dist={dist:.5f})")
            n_fail += 1
    print(f"Total matches: {n_match}, fails: {n_fail}")

df = pd.DataFrame(rows)
print(f"\nShape du DataFrame final : {df.shape}")
print(df.head(10))
print("\nValeurs manquantes par colonne :\n", df.isnull().mean())

df.to_pickle(OUT_DIR / "final_edge_dataset.pkl")
df.to_csv(OUT_DIR / "final_edge_dataset.csv", index=False)
