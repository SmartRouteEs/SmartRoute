import pickle
import numpy as np
import networkx as nx
from shapely.geometry import LineString
from tqdm import tqdm
import rasterio
from rasterio.transform import rowcol

# === Fichiers ===
GRAPH_PATH = "data/processed/graph_with_strava.gpickle"
HEATMAP_TIF = "data/strava_tiles/heatmap.tif"

# === Charger la heatmap une fois
print(f"\U0001f525 Chargement de la heatmap depuis : {HEATMAP_TIF}")
with rasterio.open(HEATMAP_TIF) as src:
    heatmap_array = src.read(1)  # on suppose intensité dans bande 1
    transform = src.transform
    nodata = src.nodata if src.nodata is not None else 0
    bounds = src.bounds

# === Charger le graphe
print(f"\U0001f4c5 Chargement du graphe : {GRAPH_PATH}")
with open(GRAPH_PATH, "rb") as f:
    G = pickle.load(f)

# === Fonction pour calculer l'intensité d'une arête

def get_intensity(line: LineString) -> float:
    if line.is_empty:
        return 0.0

    samples = [line.interpolate(t, normalized=True).coords[0] for t in np.linspace(0, 1, num=5)]
    values = []

    for lon, lat in samples:
        if not (bounds.left <= lon <= bounds.right and bounds.bottom <= lat <= bounds.top):
            continue
        try:
            row, col = rowcol(transform, lon, lat)
            val = heatmap_array[row, col]
            if val > 0:
                values.append(val)
        except IndexError:
            continue

    return float(np.mean(values)) if values else 0.0

# === Application à toutes les arêtes
print("\u2699\ufe0f Calcul des intensités...")
processed = 0
no_geom = 0

for u, v, k, data in tqdm(G.edges(keys=True, data=True)):
    geom = data.get("geometry")
    if isinstance(geom, LineString):
        data["strava"] = get_intensity(geom)
        processed += 1
    else:
        data["strava"] = 0.0
        no_geom += 1

print(f"\u2705 Arêtes traitées : {processed}")
print(f"\u26d4 Arêtes sans géométrie : {no_geom}")

# === Sauvegarde
with open(GRAPH_PATH, "wb") as f:
    pickle.dump(G, f)

print(f"\U0001f4be Graphe enrichi sauvegardé : {GRAPH_PATH}")