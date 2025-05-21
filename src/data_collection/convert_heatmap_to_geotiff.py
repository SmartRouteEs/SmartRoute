import numpy as np
from PIL import Image
import rasterio
from rasterio.transform import from_bounds
import os

# === Coordonnées et dimensions
CENTER_LAT = 48.4
CENTER_LON = 2.4
AREA_KM = 130  # correspond à ton image téléchargée

# === Fichiers
INPUT_PNG = "data/processed/heatmap_130km_48_4_2_4.png"
OUTPUT_TIF = "data/strava_tiles/heatmap.tif"

# === Résolution approximative
deg_per_km = 1.0 / 111  # ~0.009°
pixel_size = (AREA_KM * deg_per_km) / 256  # pour 256 px de base

# === Charger l’image PNG
img = Image.open(INPUT_PNG).convert("RGBA")
width, height = img.size

# === Définir la transformation spatiale (géoréférencement)
transform = from_bounds(
    CENTER_LON - (width / 2) * pixel_size,
    CENTER_LAT - (height / 2) * pixel_size,
    CENTER_LON + (width / 2) * pixel_size,
    CENTER_LAT + (height / 2) * pixel_size,
    width,
    height
)

# === Convertir chaque canal en numpy array
r, g, b, a = [np.array(c) for c in img.split()]

# === Écriture GeoTIFF
os.makedirs(os.path.dirname(OUTPUT_TIF), exist_ok=True)
with rasterio.open(
    OUTPUT_TIF,
    "w",
    driver="GTiff",
    height=height,
    width=width,
    count=4,
    dtype="uint8",
    crs="EPSG:4326",
    transform=transform
) as dst:
    dst.write(r, 1)
    dst.write(g, 2)
    dst.write(b, 3)
    dst.write(a, 4)

print(f"✅ Fichier GeoTIFF généré : {OUTPUT_TIF}")
