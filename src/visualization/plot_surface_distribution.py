import pickle
import matplotlib.pyplot as plt
from collections import Counter

# Charger le graphe filtré
with open("data/processed/osm_graph_filtered.gpickle", "rb") as f:
    G = pickle.load(f)

# Compter les types de surface
surfaces = [d.get("surface", "unknown") for _, _, d in G.edges(data=True)]
surface_counts = Counter(surfaces)

# Tri par fréquence
sorted_surfaces = dict(sorted(surface_counts.items(), key=lambda x: x[1], reverse=True))

# Affichage
plt.figure(figsize=(12, 6))
plt.bar(sorted_surfaces.keys(), sorted_surfaces.values(), color='orange')
plt.xticks(rotation=45, ha='right')
plt.title("Distribution des types de surface")
plt.xlabel("Type de surface")
plt.ylabel("Nombre d’arêtes")
plt.tight_layout()
plt.grid(True, axis='y')
plt.show()
