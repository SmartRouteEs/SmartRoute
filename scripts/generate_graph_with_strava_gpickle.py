import pickle
import numpy as np
import networkx as nx
from shapely.geometry import LineString
from tqdm import tqdm
import rasterio
from rasterio.transform import rowcol

# === Chemins corrigés ===
GRAPH_INPUT = "data/processed/graph_with_dplus.gpickle"
GRAPH_OUTPUT = "data/processed/graph_with_strava_and_dplus.gpickle"
HEATMAP_TIF = "data/strava_tiles/heatmap.tif"

# === Chargement heatmap
print(f"🔥 Chargement de la heatmap depuis : {HEATMAP_TIF}")
with rasterio.open(HEATMAP_TIF) as src:
    heatmap_array = src.read(1)
    transform = src.transform
    nodata = src.nodata if src.nodata is not None else 0
    bounds = src.bounds

# === Chargement graphe
print(f"📥 Chargement du graphe : {GRAPH_INPUT}")
with open(GRAPH_INPUT, "rb") as f:
    G = pickle.load(f)

# === Calcul de l'intensité popularity (ex-strava) d'une arête
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
print("⚙️  Calcul des intensités popularity...")
processed = 0
no_geom = 0

for u, v, k, data in tqdm(G.edges(keys=True, data=True)):
    geom = data.get("geometry")
    if isinstance(geom, LineString):
        data["popularity"] = get_intensity(geom)   # CHANGEMENT ICI
        processed += 1
    else:
        data["popularity"] = 0.0                   # CHANGEMENT ICI
        no_geom += 1

print(f"✅ Arêtes traitées : {processed}")
print(f"⛔ Arêtes sans géométrie : {no_geom}")

# === Sauvegarde
with open(GRAPH_OUTPUT, "wb") as f:
    pickle.dump(G, f)

print(f"💾 Graphe enrichi sauvegardé : {GRAPH_OUTPUT}")
