import networkx as nx
from pathlib import Path

# Fichier d'entrée
GRAPHML_PATH = Path("data/raw_osm/osm_graph_bike_45km_48.55_2.8.graphml")

# Fichier de sortie
FILTERED_GRAPHML_PATH = Path("data/processed/osm_graph_filtered.graphml")

# Types de routes à garder
VALID_HIGHWAY_TYPES = {
    "residential", "primary", "secondary", "tertiary",
    "cycleway", "footway", "path", "track", "unclassified", "service"
}

def load_graph(path):
    print(f"Chargement du graphe depuis {path}")
    return nx.read_graphml(path)

def filter_graph(G):
    edges_valides = [
        (u, v, k) for u, v, k, d in G.edges(data=True, keys=True)
        if "highway" in d and d["highway"] in VALID_HIGHWAY_TYPES
    ]
    return G.edge_subgraph(edges_valides).copy()


def save_graph(G, path):
    print(f"Sauvegarde du graphe filtré vers {path}")
    nx.write_graphml(G, path)

if __name__ == "__main__":
    G = load_graph(GRAPHML_PATH)
    G_filtered = filter_graph(G)
    save_graph(G_filtered, FILTERED_GRAPHML_PATH)
    print(f"Graphe filtré : {G_filtered.number_of_nodes()} nœuds, {G_filtered.number_of_edges()} arêtes")
