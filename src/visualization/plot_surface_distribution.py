import pickle
import matplotlib.pyplot as plt
from collections import Counter
import os

GRAPH_PATH = "data/processed/graph_with_strava_and_dplus.gpickle"

with open(GRAPH_PATH, "rb") as f:
    G = pickle.load(f)

# Extraire les surfaces valides
surfaces = [
    d.get("surface", "unknown")
    for _, _, _, d in G.edges(keys=True, data=True)
    if d.get("surface", "unknown") != "unknown"
]

surface_counts = Counter(surfaces)

if not surface_counts:
    print("⚠️ Aucune surface trouvée.")
else:
    sorted_surfaces = dict(sorted(surface_counts.items(), key=lambda x: x[1], reverse=True))

    plt.figure(figsize=(12, 6))
    plt.bar(sorted_surfaces.keys(), sorted_surfaces.values(), color='orange')
    plt.xticks(rotation=45, ha='right')
    plt.title("Répartition des types de surfaces")
    plt.xlabel("Type de surface")
    plt.ylabel("Nombre d’arêtes")
    plt.tight_layout()
    plt.grid(True, axis='y')

    os.makedirs("outputs", exist_ok=True)
    plt.savefig("outputs/surface_distribution.png")
    print("✅ Graphe sauvegardé : outputs/surface_distribution.png")
