import osmnx as ox
import networkx as nx
from pathlib import Path
import os
import pickle

def download_osm_graph(filepath: str, center: tuple, dist: int, network_type="bike"):
    filepath = Path(filepath)
    graphml_path = filepath.with_suffix(".graphml")
    gpickle_path = filepath.with_suffix(".gpickle")
    render_path = filepath.with_suffix(".png")

    print("📡 Téléchargement du graphe brut depuis OSM...")
    G = ox.graph.graph_from_point(
        center_point=center,
        dist=dist,
        network_type=network_type,
        simplify=True
    )

    # 📷 Sauvegarde du rendu
    ox.plot_graph(G, show=False, save=True, filepath=render_path, dpi=150)
    print(f"🖼️ Graphe dessiné : {render_path}")

    # 💾 Sauvegarde GraphML
    ox.save_graphml(G, graphml_path)
    print(f"💾 Graphe sauvegardé : {graphml_path}")

    # 💾 Sauvegarde GPickle
    with open(gpickle_path, "wb") as f:
        pickle.dump(G, f)
    print(f"✅ Graphe sauvegardé au format pickle : {gpickle_path}")

    return G

# Exemple d’utilisation
if __name__ == "__main__":
    os.makedirs("data/raw_osm", exist_ok=True)

    G = download_osm_graph(
        filepath="data/raw_osm/osm_graph_paris_bike_3km",
        center=(48.85, 2.35),  # 📍 Paris centre
        dist=3000,
        network_type="bike"
    )
import osmnx as ox
import networkx as nx
from pathlib import Path
import os
import pickle

def download_osm_graph(filepath: str, center: tuple, dist: int, network_type="bike"):
    filepath = Path(filepath)
    graphml_path = filepath.with_suffix(".graphml")
    gpickle_path = filepath.with_suffix(".gpickle")
    render_path = filepath.with_suffix(".png")

    print("📡 Téléchargement du graphe brut depuis OSM...")
    G = ox.graph.graph_from_point(
        center_point=center,
        dist=dist,
        network_type=network_type,
        simplify=True
    )

    # 📷 Sauvegarde du rendu
    ox.plot_graph(G, show=False, save=True, filepath=render_path, dpi=150)
    print(f"🖼️ Graphe dessiné : {render_path}")

    # 💾 Sauvegarde GraphML
    ox.save_graphml(G, graphml_path)
    print(f"💾 Graphe sauvegardé : {graphml_path}")

    # 💾 Sauvegarde GPickle
    with open(gpickle_path, "wb") as f:
        pickle.dump(G, f)
    print(f"✅ Graphe sauvegardé au format pickle : {gpickle_path}")

    return G

# Exemple d’utilisation
if __name__ == "__main__":
    os.makedirs("data/raw_osm", exist_ok=True)

    G = download_osm_graph(
        filepath="data/raw_osm/osm_graph_paris_bike_3km",
        center=(48.85, 2.35),  # 📍 Paris centre
        dist=3000,
        network_type="bike"
    )
