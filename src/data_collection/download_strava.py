import os
import requests
from PIL import Image
import io
import math

from src.data_collection.tile_utils import deg2num, get_zoom_for_area

def download_heatmap_area(lat, lon, area_km=10, max_tiles=100, activity="run", output_path=None):
    """
    Télécharge une image heatmap Strava centrée sur (lat, lon) couvrant area_km x area_km.
    Les tuiles sont mises en cache dans data/strava_tiles/.
    L'image finale est enregistrée automatiquement dans data/processed/
    avec un nom basé sur la coordonnée et la taille de la zone.
    """
    zoom = get_zoom_for_area(area_km=area_km, max_tiles=max_tiles, lat=lat)
    print(f"Zoom sélectionné : {zoom}")

    center_x, center_y = deg2num(lat, lon, zoom)
    tile_km = 40075 * abs(math.cos(math.radians(lat))) / (2 ** zoom)
    nb_tiles = int(area_km / tile_km / 2)

    tile_size = 256
    total_width = tile_size * (2 * nb_tiles + 1)
    total_height = tile_size * (2 * nb_tiles + 1)
    combined_image = Image.new("RGBA", (total_width, total_height))

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for dx in range(-nb_tiles, nb_tiles + 1):
        for dy in range(-nb_tiles, nb_tiles + 1):
            x = center_x + dx
            y = center_y + dy
            url = f"https://strava-heatmap.tiles.freemap.sk/{activity}/hot/{zoom}/{x}/{y}.png"
            tile_path = f"data/strava_tiles/{zoom}/{x}/{y}.png"

            try:
                if os.path.exists(tile_path):
                    tile_image = Image.open(tile_path)
                    print(f"Tuile en cache : {tile_path}")
                else:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    tile_image = Image.open(io.BytesIO(response.content))
                    os.makedirs(os.path.dirname(tile_path), exist_ok=True)
                    tile_image.save(tile_path)
                    print(f"Téléchargé et sauvegardé : {tile_path}")

                pos_x = (dx + nb_tiles) * tile_size
                pos_y = (dy + nb_tiles) * tile_size
                combined_image.paste(tile_image, (pos_x, pos_y))

            except Exception as e:
                print(f"Erreur pour {url} : {e}")
                continue

    # Génération automatique du nom de l'image finale si non fourni
    if output_path is None:
        safe_lat = str(round(lat, 5)).replace('.', '_')
        safe_lon = str(round(lon, 5)).replace('.', '_')
        filename = f"heatmap_{area_km}km_{safe_lat}_{safe_lon}.png"
        output_path = os.path.join("data", "processed", filename)

    # Création du dossier si besoin et sauvegarde
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    combined_image.save(output_path)
    print(f"Image finale sauvegardée : {output_path}")

if __name__ == "__main__":
    download_heatmap_area(
        lat=43.48333,
        lon=3.66667,
        area_km=50,
        max_tiles=100,
        activity="run"
    )
