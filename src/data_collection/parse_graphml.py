from pathlib import Path
import networkx as nx
import pandas as pd
import math
import pickle
from tqdm import tqdm

# === Chemins ===
GRAPHML_INPUT = Path("data/raw_osm/osm_graph_bike_45km_48.55_2.8.graphml")
GRAPHML_OUTPUT = Path("data/processed/osm_graph_filtered.graphml")
GPICKLE_OUTPUT = Path("data/processed/osm_graph_filtered.gpickle")
POP_CSV = Path("data/processed/postal_population.csv")
GRID_CSV = Path("data/raw/postal_grid.csv")

# === Types de routes à garder
VALID_HIGHWAY_TYPES = {
    "residential", "primary", "secondary", "tertiary",
    "cycleway", "footway", "path", "track", "unclassified", "service"
}

SURFACE_DEFAULTS = {
    "residential": "asphalt",
    "primary": "asphalt",
    "secondary": "asphalt",
    "tertiary": "asphalt",
    "cycleway": "paved",
    "footway": "paved",
    "path": "dirt",
    "track": "gravel",
    "unclassified": "asphalt",
    "service": "asphalt"
}

# === Charger population
def load_population_csv(path: Path):
    if not path.exists():
        print(f"⚠️ Fichier population introuvable : {path}")
        return {}
    df = pd.read_csv(path, dtype={"postal_code": str})
    return dict(zip(df["postal_code"], df["population"]))

# === Charger grille lat/lon → code postal
def load_postal_grid(path: Path):
    if not path.exists():
        print(f"⚠️ Grille postale introuvable : {path}")
        return {}
    df = pd.read_csv(path)
    return {
        (round(row["lat"], 4), round(row["lon"], 4)): str(row["postal_code"]).split('.')[0].zfill(5)
        for _, row in df.iterrows()
    }

# === Fonction pour arrondir à la grille
def round_coord(coord, step=0.01):
    return round(math.floor(coord / step) * step, 4)

def get_postal_from_grid(lat, lon, grid_dict):
    key = (round_coord(lat), round_coord(lon))
    return grid_dict.get(key, "unknown")

def is_valid_highway(hw):
    if isinstance(hw, list):
        return any(h in VALID_HIGHWAY_TYPES for h in hw)
    return hw in VALID_HIGHWAY_TYPES

def get_surface(d):
    surface = d.get("surface", "unknown")
    if surface != "unknown":
        return surface
    hw = d.get("highway")
    if isinstance(hw, list):
        for h in hw:
            if h in SURFACE_DEFAULTS:
                return SURFACE_DEFAULTS[h]
    elif hw in SURFACE_DEFAULTS:
        return SURFACE_DEFAULTS[hw]
    return "unknown"

def safe_get_coords(G, u, v):
    try:
        lon = (float(G.nodes[u]["x"]) + float(G.nodes[v]["x"])) / 2
        lat = (float(G.nodes[u]["y"]) + float(G.nodes[v]["y"])) / 2
        return lat, lon
    except KeyError:
        return None, None

# === Traitement principal
def filter_graph(G, population_dict, grid_dict):
    edges_valides = []
    for u, v, k, d in tqdm(G.edges(data=True, keys=True), desc="🔍 Filtrage du graphe"):
        if not is_valid_highway(d.get("highway")):
            continue

        d["surface"] = get_surface(d)

        lat, lon = safe_get_coords(G, u, v)
        if lat is None or lon is None:
            d["postal_code"] = "unknown"
            d["population"] = 0
            edges_valides.append((u, v, k))
            continue

        postal_code = get_postal_from_grid(lat, lon, grid_dict)
        postal_code = str(postal_code).split('.')[0].zfill(5)

        d["postal_code"] = postal_code
        d["population"] = population_dict.get(postal_code, 0)

        edges_valides.append((u, v, k))

    return G.edge_subgraph(edges_valides).copy()

# === MAIN ===
if __name__ == "__main__":
    print("📥 Chargement du graphe brut...")
    G = nx.read_graphml(GRAPHML_INPUT)

    print("📊 Chargement des populations...")
    population_dict = load_population_csv(POP_CSV)

    print("🗺️ Chargement de la grille lat/lon → code postal...")
    grid_dict = load_postal_grid(GRID_CSV)

    print("🔧 Filtrage et enrichissement des arêtes...")
    G_filtered = filter_graph(G, population_dict, grid_dict)

    print(f"💾 Sauvegarde rapide (pickle) → {GPICKLE_OUTPUT}")
    with open(GPICKLE_OUTPUT, "wb") as f:
        pickle.dump(G_filtered, f)

    print(f"💾 Sauvegarde lisible (graphml) → {GRAPHML_OUTPUT}")
    nx.write_graphml(G_filtered, GRAPHML_OUTPUT)

    print("✅ Terminé.")
