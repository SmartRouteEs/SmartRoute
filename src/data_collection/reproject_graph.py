import pickle
import osmnx as ox
from pathlib import Path

# Chemins
INPUT = Path("data/processed/graph_with_strava_and_dplus.gpickle")
OUTPUT = Path("data/processed/graph_wgs84.gpickle")

# Chargement du graphe original
with open(INPUT, "rb") as f:
    G = pickle.load(f)

print(f"> CRS original : {G.graph.get('crs')}")

# Reprojection vers latitude/longitude (EPSG:4326)
G_proj = ox.project_graph(G, to_crs="EPSG:4326")

print(f"> Nouveau CRS : {G_proj.graph.get('crs')}")

# Sauvegarde du graphe reprojeté
with open(OUTPUT, "wb") as f:
    pickle.dump(G_proj, f)

print("✓ Graphe reprojeté sauvegardé dans", OUTPUT)
