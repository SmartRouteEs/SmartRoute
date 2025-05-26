import os
import pickle
from pathlib import Path
import osmnx as ox
import networkx as nx
import math

def download_osm_graph(filepath: str, center: tuple, side_km: int, network_type="bike"):
    filepath = Path(filepath)
    graphml_path = filepath.with_suffix(".graphml")
    gpickle_path = filepath.with_suffix(".gpickle")
    render_path = filepath.with_suffix(".png")

    # === Conversion en degrés
    lat, lon = center
    deg_lat = (side_km / 2) / 111.0
    deg_lon = (side_km / 2) / (111.0 * math.cos(math.radians(lat)))

    north = lat + deg_lat
    south = lat - deg_lat
    east = lon + deg_lon
    west = lon - deg_lon

    print("📦 Bounding Box :")
    print(f"  Latitude  : {south:.5f} → {north:.5f}")
    print(f"  Longitude : {west:.5f} → {east:.5f}")

    # === Téléchargement du graphe (bbox)
    print("📡 Téléchargement du graphe brut depuis OSM...")
    G = ox.graph.graph_from_bbox(
    north=north,
    south=south,
    east=east,
    west=west,
    network_type=network_type,
    simplify=True
)

    # 📷 Sauvegarde du rendu visuel
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
        filepath="data/raw_osm/osm_graph_zone_interet",
        center=(48.55, 2.8),
        dist=65000,  # ✅ pour une zone ~90x90 km, rayon de 65 km.
        network_type="bike"
    )
