import pickle

GRAPH_PATH = "data/processed/graph_with_strava.gpickle"

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


import random
from shapely.geometry import LineString

with open("data/processed/graph_with_strava.gpickle", "rb") as f:
    G = pickle.load(f)

edges = list(G.edges(keys=True, data=True))
random.shuffle(edges)

print("🔎 Exemple d'arêtes avec intensité :\n")
for u, v, k, d in edges[:5]:
    print(f"{u} → {v} [{k}]")
    print(f"  ↪️  strava : {d.get('strava')}")
    if isinstance(d.get("geometry"), LineString):
        print(f"  📐 geom   : {d['geometry'].wkt[:80]}...")
    print("-" * 40)
