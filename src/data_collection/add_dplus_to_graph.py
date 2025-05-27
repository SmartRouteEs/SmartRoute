import pickle
from pathlib import Path
from shapely.geometry import LineString
from tqdm import tqdm
import rasterio
from rasterio.merge import merge
from rasterio.transform import rowcol
from pyproj import Transformer

# === Fichiers
GRAPH_INPUT = Path("data/processed/graph_with_strava.gpickle")
GRAPH_OUTPUT = Path("data/processed/graph_with_strava_and_dplus.gpickle")
DEM_FOLDER = Path("data/dem/tif")

# === Préparation de la reprojection EPSG:4326 (lon, lat) → EPSG:2154 (LAMBERT-93)
transformer = Transformer.from_crs("EPSG:4326", "EPSG:2154", always_xy=True)

# === Fusion des fichiers DEM
print(f"🗺️  Chargement des fichiers DEM dans : {DEM_FOLDER}")
tif_files = list(DEM_FOLDER.glob("*.tif"))
if not tif_files:
    raise FileNotFoundError("❌ Aucun fichier .tif trouvé dans data/dem/tif/")

srcs = [rasterio.open(tif) for tif in tif_files]
mosaic, out_transform = merge(srcs)
nodata = srcs[0].nodata if srcs[0].nodata is not None else -9999
bounds = rasterio.transform.array_bounds(mosaic.shape[1], mosaic.shape[2], out_transform)

# === Chargement du graphe
print(f"📥 Chargement du graphe : {GRAPH_INPUT}")
with open(GRAPH_INPUT, "rb") as f:
    G = pickle.load(f)

print("⛰️  Calcul du D+ sur chaque arête...")

processed = 0
for u, v, k, data in tqdm(G.edges(data=True, keys=True)):
    geom = data.get("geometry")
    if isinstance(geom, LineString):
        coords = list(geom.coords)
        points = [(lat, lon) for lon, lat in coords]  # inversion
        elevations = []

        for lat, lon in points:
            x93, y93 = transformer.transform(lon, lat)

            if not (bounds[0] <= x93 <= bounds[2] and bounds[1] <= y93 <= bounds[3]):
                elevations.append(0.0)
                continue
            try:
                row, col = rowcol(out_transform, x93, y93)
                elev = mosaic[0, row, col]
                if elev == nodata or elev is None:
                    elevations.append(0.0)
                else:
                    elevations.append(float(elev))
                    print(f"↳ Point ({lon:.4f}, {lat:.4f}) → x={x93:.2f}, y={y93:.2f} → elev={elev:.2f}")
            except Exception as e:
                print(f"⚠️ Erreur sur ({lon}, {lat}) : {e}")
                elevations.append(0.0)

        dplus = sum(max(0, e2 - e1) for e1, e2 in zip(elevations[:-1], elevations[1:]))
        data["dplus"] = round(dplus, 2)
        processed += 1
    else:
        data["dplus"] = 0.0

print(f"✅ Arêtes traitées avec D+ : {processed}")

# === Sauvegarde
print(f"💾 Sauvegarde du graphe enrichi avec D+ : {GRAPH_OUTPUT}")
with open(GRAPH_OUTPUT, "wb") as f:
    pickle.dump(G, f)

print("✅ Terminé.")
