import pickle
import matplotlib.pyplot as plt

# Charger le graphe filtré
with open("data/processed/osm_graph_filtered.gpickle", "rb") as f:
    G = pickle.load(f)

# 💡 Debug : afficher un exemple d'arête
for _, _, d in G.edges(data=True):
    print("Postal:", d.get("postal_code"), "| Population:", d.get("population"))
    break  # on n'affiche qu'une seule ligne

# Extraire les populations des arêtes
populations = [d.get("population", 0) for _, _, d in G.edges(data=True)]
populations = [p for p in populations if isinstance(p, (int, float)) and p > 0]

# Vérification
print(f"✅ Nombre d’arêtes avec population > 0 : {len(populations)}")

# Affichage
plt.figure(figsize=(10, 6))

if populations:
    plt.hist(populations, bins=50, log=True, color='skyblue', edgecolor='black')
    plt.ylabel("Nombre d’arêtes (échelle log)")
else:
    plt.text(0.5, 0.5, "Aucune population > 0", ha="center", va="center", fontsize=14)
    plt.ylabel("")

plt.title("Distribution des populations des zones traversées (code postal)")
plt.xlabel("Population")
plt.grid(True)
plt.tight_layout()
plt.show()
