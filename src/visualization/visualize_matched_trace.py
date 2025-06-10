import json
import matplotlib.pyplot as plt
import osmnx as ox
from shapely.geometry import LineString
from pathlib import Path
import pickle
import polyline

GRAPH_FILE = "data/processed/graph_wgs84.gpickle"
MATCHED_DIR = Path("data/matched_traces")

# Mots-clés de traces déjà vues à exclure
SEEN_KEYWORDS = [
    "avon",
    "rando-vtt-fontainebleau-et-milly",
    "fontaine-desiree-et-mare-de-bouligny",
    "fontainebleau-sens-avoisines",
    "cghvl",
    "vtt-roulant-sur-petits-chemins"
]

def load_graph(path):
    with open(path, "rb") as f:
        return pickle.load(f)

def extract_shape_points(data):
    legs = data.get("trip", {}).get("legs", [])
    all_points = []
    for leg in legs:
        shape_raw = leg.get("shape")
        if not shape_raw:
            continue
        if isinstance(shape_raw, str):
            decoded = polyline.decode(shape_raw)
            if max(abs(lat) for lat, _ in decoded) > 90:
                decoded = [(lat / 10, lon / 10) for lat, lon in decoded]
            all_points.extend(decoded)
        elif isinstance(shape_raw, list):
            all_points.extend(shape_raw)
    return all_points

def should_exclude(name):
    name = name.lower()
    return any(keyword in name for keyword in SEEN_KEYWORDS)

def plot_matched_trace(matched_json_path):
    with open(matched_json_path, "r") as f:
        data = json.load(f)
    shape_points = extract_shape_points(data)
    if not shape_points:
        print(f"❌ Trace vide ou invalide : {matched_json_path}")
        return

    G = load_graph(GRAPH_FILE)
    shape_line = LineString([(lon, lat) for lat, lon in shape_points])

    fig, ax = ox.plot_graph(G, show=False, close=False, node_size=0, edge_color="lightgray")

    xs, ys = shape_line.xy
    ax.plot(xs, ys, color="red", linewidth=2, label=Path(matched_json_path).stem)

    minx, miny, maxx, maxy = shape_line.bounds
    buffer = 0.005
    ax.set_xlim(minx - buffer, maxx + buffer)
    ax.set_ylim(miny - buffer, maxy + buffer)

    ax.legend()
    plt.title(f"Trace matched - {Path(matched_json_path).stem}")
    plt.tight_layout()
    plt.show()

def main():
    all_jsons = list(MATCHED_DIR.glob("*.json"))
    candidates = []

    for path in all_jsons:
        if should_exclude(path.stem):
            continue
        with open(path, "r") as f:
            data = json.load(f)
        points = extract_shape_points(data)
        if points:
            candidates.append((len(points), path))

    # Affiche les 10 premiers candidats pour vérification
    print("Candidats après filtre :")
    for _, p in sorted(candidates, reverse=True)[:10]:
        print(" -", p.name)

    top_3 = sorted(candidates, reverse=True)[:3]
    for _, trace_path in top_3:
        print(f"Affichage de la trace : {trace_path.name}")
        plot_matched_trace(trace_path)

if __name__ == "__main__":
    main()
