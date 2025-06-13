import pickle
from pathlib import Path

GRAPH_FILE = "data/processed/osm_graph_filtered_clean.gpickle"
CLEAN_DIR = Path("data/gpx_clean")

# Affiche les 5 premiers points de la première trace trouvée
def print_first_points():
    traces = list(CLEAN_DIR.glob("*.pkl"))
    if not traces:
        print("Aucune trace trouvée.")
        return
    with open(traces[0], "rb") as f:
        trace = pickle.load(f)
    print(f"Fichier testé : {traces[0].name}")
    print("Premiers points de la trace (lat, lon) :")
    for pt in trace[:5]:
        print(pt)
    lats = [pt[0] for pt in trace]
    lons = [pt[1] for pt in trace]
    print(f"Latitude : min={min(lats):.4f}, max={max(lats):.4f}")
    print(f"Longitude : min={min(lons):.4f}, max={max(lons):.4f}")
    return lats, lons

# Affiche la bounding box du graphe
def print_graph_bbox():
    import pickle
    with open(GRAPH_FILE, "rb") as f:
        G = pickle.load(f)
    xs = [d["x"] for _, d in G.nodes(data=True)]
    ys = [d["y"] for _, d in G.nodes(data=True)]
    print("\nGraphe OSM :")
    print(f"BBox x (longitude): min={min(xs):.4f}, max={max(xs):.4f}")
    print(f"BBox y (latitude) : min={min(ys):.4f}, max={max(ys):.4f}")
    return xs, ys

if __name__ == "__main__":
    lats, lons = print_first_points()
    xs, ys = print_graph_bbox()

    # Vérifie si la trace est dans la bbox
    if lats and lons and xs and ys:
        out_lat = any(lat < min(ys) or lat > max(ys) for lat in lats)
        out_lon = any(lon < min(xs) or lon > max(xs) for lon in lons)
        if out_lat or out_lon:
            print("\n⚠️  Certains points de la trace sont en dehors de la bbox du graphe OSM !")
        else:
            print("\n✅ Tous les points de la trace sont bien dans la bbox OSM.")
