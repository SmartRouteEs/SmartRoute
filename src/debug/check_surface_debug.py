import pickle

with open("data/processed/graph_with_strava.gpickle", "rb") as f:
    G = pickle.load(f)

has_population = 0
non_zero = 0

for _, _, _, d in G.edges(keys=True, data=True):
    if "population" in d:
        has_population += 1
        if d["population"] > 0:
            non_zero += 1
            print(d["postal_code"], d["population"])
            break

print(f"✅ Arêtes avec un champ 'population' : {has_population}")
print(f"✅ Arêtes avec population > 0        : {non_zero}")
