import pickle
import random
from shapely.geometry import LineString
from pathlib import Path

GRAPH_PATH = Path("data/processed/graph_with_strava_and_dplus.gpickle")

if not GRAPH_PATH.exists():
    raise FileNotFoundError(f"❌ Fichier introuvable : {GRAPH_PATH}")

with open(GRAPH_PATH, "rb") as f:
    G = pickle.load(f)

has_strava = 0
nonzero = 0
total = G.number_of_edges()

for _, _, _, data in G.edges(keys=True, data=True):
    if "strava" in data:
        has_strava += 1
        if data["strava"] > 0:
            nonzero += 1

print(f"✅ Arêtes avec un champ 'strava' : {has_strava}/{total}")
print(f"✅ Arêtes avec intensité > 0     : {nonzero}")

# Affichage d'exemples
edges = list(G.edges(keys=True, data=True))
random.shuffle(edges)

print("\n🔎 Exemple d'arêtes avec intensité :\n")
count = 0
for u, v, k, d in edges:
    if d.get("strava", 0) > 0:
        print(f"{u} → {v} [{k}]")
        print(f"  ↪️  strava : {d['strava']}")
        if isinstance(d.get("geometry"), LineString):
            print(f"  📐 geom   : {d['geometry'].wkt[:80]}...")
        print("-" * 40)
        count += 1
        if count >= 5:
            break
