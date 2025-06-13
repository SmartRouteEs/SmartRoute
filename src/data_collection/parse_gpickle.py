import pickle
import networkx as nx
from pathlib import Path
from tqdm import tqdm
from shapely.geometry import LineString

# === Chemins ===
GPICKLE_INPUT = Path("data/raw_osm/osm_graph_zone_interet.gpickle")
GPICKLE_OUTPUT = Path("data/processed/osm_graph_filtered_clean.gpickle")

# === Types de routes à exclure (grands axes interdits aux vélos)
EXCLUDED_HIGHWAY_TYPES = {
    "motorway", "motorway_link", "trunk", "trunk_link"
}

# === Types de routes explicitement inclus
INCLUDED_HIGHWAY_TYPES = {
    "residential", "primary", "secondary", "tertiary",
    "cycleway", "footway", "path", "track", "unclassified", "service",
    "living_street", "pedestrian", "bridleway", "steps"
}

# === Valeurs par défaut de surface
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
    "service": "asphalt",
    "living_street": "paved",
    "pedestrian": "paved",
    "bridleway": "dirt",
    "steps": "stone"
}

def is_valid_highway(hw):
    if hw is None:
        return False
    if isinstance(hw, list):
        return any(h in INCLUDED_HIGHWAY_TYPES and h not in EXCLUDED_HIGHWAY_TYPES for h in hw)
    return hw in INCLUDED_HIGHWAY_TYPES and hw not in EXCLUDED_HIGHWAY_TYPES

def get_surface(d):
    s = d.get("surface", "unknown")
    if s != "unknown":
        return s
    hw = d.get("highway")
    if isinstance(hw, list):
        for h in hw:
            if h in SURFACE_DEFAULTS:
                return SURFACE_DEFAULTS[h]
    elif hw in SURFACE_DEFAULTS:
        return SURFACE_DEFAULTS[hw]
    return "unknown"

def filter_graph(G):
    edges_valides = []
    total = 0

    for u, v, k, d in tqdm(G.edges(data=True, keys=True), desc="🔧 Filtrage et enrichissement"):
        total += 1
        if not is_valid_highway(d.get("highway")):
            continue
        d["surface"] = get_surface(d)
        d["edge_id"] = (u, v, k)  # <<<< AJOUT DU TUPLE UNIQUE ICI
        edges_valides.append((u, v, k))

    print(f"✅ Arêtes conservées : {len(edges_valides)} / {total}")

    if not edges_valides:
        print("⚠️ Aucun segment n'a passé le filtre — on garde tout le graphe brut.")
        return G

    G_filtered = G.edge_subgraph(edges_valides).copy()

    # Ajout des géométries manquantes
    added = 0
    for u, v, k, data in G_filtered.edges(keys=True, data=True):
        if "geometry" not in data or not isinstance(data["geometry"], LineString):
            try:
                x1, y1 = G_filtered.nodes[u]["x"], G_filtered.nodes[u]["y"]
                x2, y2 = G_filtered.nodes[v]["x"], G_filtered.nodes[v]["y"]
                data["geometry"] = LineString([(x1, y1), (x2, y2)])
                added += 1
            except KeyError:
                continue
    print(f"✅ Géométries ajoutées à {added} arêtes")

    print("🔗 Vérification de la connectivité...")
    components = list(nx.connected_components(G_filtered.to_undirected()))
    largest_nodes = max(components, key=len)
    G_filtered = G_filtered.subgraph(largest_nodes).copy()
    print(f"✅ Composante principale conservée : {len(largest_nodes)} nœuds")

    return G_filtered

# === MAIN ===
if __name__ == "__main__":
    print("📥 Chargement du graphe brut .gpickle...")
    with open(GPICKLE_INPUT, "rb") as f:
        G = pickle.load(f)

    print("🧠 Enrichissement...")
    G_filtered = filter_graph(G)

    print(f"💾 Sauvegarde du graphe enrichi : {GPICKLE_OUTPUT}")
    with open(GPICKLE_OUTPUT, "wb") as f:
        pickle.dump(G_filtered, f)

    print("✅ Terminé.")
