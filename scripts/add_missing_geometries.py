import pickle
from pathlib import Path
import networkx as nx
from shapely.geometry import LineString

GRAPH_PATH = Path("data/processed/graph_with_strava.gpickle")

# 🔄 Chargement
print(f"📥 Chargement du graphe : {GRAPH_PATH}")
with open(GRAPH_PATH, "rb") as f:
    G = pickle.load(f)

# 🔧 Ajout manuel des géométries manquantes
added = 0
for u, v, k, data in G.edges(keys=True, data=True):
    if "geometry" not in data or not isinstance(data["geometry"], LineString):
        try:
            x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"]
            x2, y2 = G.nodes[v]["x"], G.nodes[v]["y"]
            data["geometry"] = LineString([(x1, y1), (x2, y2)])
            added += 1
        except KeyError:
            continue  # ignorer si coordonnées manquantes

print(f"✅ Géométries ajoutées à {added} arêtes")

# 💾 Sauvegarde
with open(GRAPH_PATH, "wb") as f:
    pickle.dump(G, f)

print(f"💾 Graphe mis à jour sauvegardé dans : {GRAPH_PATH}")
