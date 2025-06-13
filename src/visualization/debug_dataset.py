import pickle

GRAPH_PATH = "data/processed/graph_with_strava_and_dplus.gpickle"

with open(GRAPH_PATH, "rb") as f:
    G = pickle.load(f)

count_none_dplus = 0
count_none_dist = 0
count_none_pop = 0
for u, v, k, data in G.edges(keys=True, data=True):
    if data.get("dplus") is None:
        count_none_dplus += 1
    if data.get("distance") is None:
        count_none_dist += 1
    if data.get("popularity") is None:
        count_none_pop += 1

total = G.number_of_edges()
print(f"Total edges: {total}")
print(f"Edges with dplus=None: {count_none_dplus}")
print(f"Edges with distance=None: {count_none_dist}")
print(f"Edges with popularity=None: {count_none_pop}")

# Affiche un exemple enrichi
for u, v, k, data in G.edges(keys=True, data=True):
    if data.get("dplus") is not None and data.get("distance") is not None and data.get("popularity") is not None:
        print("\nExemple d'arête enrichie:")
        print("Edge:", (u, v, k))
        print("Attributs:", data)
        break
