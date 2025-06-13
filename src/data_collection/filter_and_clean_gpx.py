import os
import gpxpy
import pickle
from pathlib import Path
from typing import List, Tuple
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
import networkx as nx
from scipy.spatial import KDTree

# === PARAMÈTRES ===
MIN_POINTS = 10
MAX_SPEED_KMH = 50
MAX_GAP = 300  # mètres
MAX_NODE_MATCH_DIST = 100  # mètres
INTERPOLATION_DIST = 20  # mètres entre points
BOUNDING_BOX = {
    "min_lon": 2.18865,
    "max_lon": 3.411287,
    "min_lat": 48.145309,
    "max_lat": 48.954693
}

# === DOSSIERS ===
INPUT_DIR = Path("data/gpx")
OUTPUT_DIR = Path("data/gpx_clean")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# === CHARGEMENT DU GRAPHE ===
GRAPH_PATH = "data/processed/graph_with_strava_and_dplus.gpickle"
with open(GRAPH_PATH, "rb") as f:
    G = pickle.load(f)

node_coords = [(data["y"], data["x"]) for _, data in G.nodes(data=True)]
node_list = list(G.nodes)
kd_tree = KDTree(node_coords)

# === UTILS ===
def haversine(coord1, coord2):
    R = 6371000
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def find_nearest_node(coord):
    dist, idx = kd_tree.query(coord)
    node_coord = node_coords[idx]
    dist_m = haversine(coord, node_coord)
    if dist_m > MAX_NODE_MATCH_DIST:
        return None
    return node_list[idx]

def interpolate_linearly(p1, p2, step=INTERPOLATION_DIST):
    lat1, lon1 = p1
    lat2, lon2 = p2
    distance = haversine(p1, p2)
    if distance <= step:
        return []
    n = int(distance // step)
    return [(lat1 + (lat2 - lat1) * i / n, lon1 + (lon2 - lon1) * i / n) for i in range(1, n)]

def interpolate_segment(p1, p2):
    n_start = find_nearest_node(p1)
    n_end = find_nearest_node(p2)
    if n_start is None or n_end is None:
        print(f"⚠️ Aucun nœud proche : fallback interpolation")
        return interpolate_linearly(p1, p2)
    try:
        path = nx.shortest_path(G, n_start, n_end, weight='length')
        return [(G.nodes[n]['y'], G.nodes[n]['x']) for n in path[1:-1]]
    except nx.NetworkXNoPath:
        print(f"❌ Pas de chemin entre {p1} → {p2} : fallback interpolation")
        return interpolate_linearly(p1, p2)

def clean_trace(points: List[Tuple[Tuple[float, float], datetime]]) -> List[Tuple[float, float]]:
    cleaned = []
    for i, (pt, time) in enumerate(points):
        if not cleaned:
            cleaned.append((pt, time))
            continue
        dist = haversine(cleaned[-1][0], pt)
        if time and cleaned[-1][1]:
            dt = (time - cleaned[-1][1]).total_seconds()
            speed = dist / dt * 3.6 if dt > 0 else 0
        else:
            speed = 0
        if dist < MAX_GAP and speed < MAX_SPEED_KMH:
            cleaned.append((pt, time))
        elif dist >= MAX_GAP:
            print(f"🚨 Saut de {int(dist)} m entre {cleaned[-1][0]} → {pt}")
            interpolated = interpolate_segment(cleaned[-1][0], pt)
            cleaned.extend([(p, None) for p in interpolated])
            cleaned.append((pt, time))
    return [pt for pt, _ in cleaned]

# === TRAITEMENT GPX ===
for gpx_file in INPUT_DIR.glob("*.gpx"):
    print(f"\n🔄 Traitement {gpx_file.name}")
    with open(gpx_file, "r") as f:
        gpx = gpxpy.parse(f)

    all_points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if (BOUNDING_BOX["min_lat"] <= point.latitude <= BOUNDING_BOX["max_lat"] and
                    BOUNDING_BOX["min_lon"] <= point.longitude <= BOUNDING_BOX["max_lon"]):
                    all_points.append(((point.latitude, point.longitude), point.time))

    if len(all_points) < MIN_POINTS:
        print("⛔ Trop peu de points")
        continue

    cleaned_trace = clean_trace(all_points)
    if len(cleaned_trace) < MIN_POINTS:
        print("⛔ Trace nettoyée trop courte")
        continue

    out_path = OUTPUT_DIR / f"{gpx_file.stem}_cleaned.pkl"
    with open(out_path, "wb") as f:
        pickle.dump(cleaned_trace, f)
    print(f"✅ Sauvegardé : {out_path.name} ({len(cleaned_trace)} points)")
