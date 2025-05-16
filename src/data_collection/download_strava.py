import os
import requests
from PIL import Image
import io
from src.data_collection.tile_utils import deg2num, num2deg, haversine

def get_appropriate_zoom(lat, lon, target_km=5):
    for zoom in range(10, 16):
        xtile, ytile = deg2num(lat, lon, zoom)
        lat_nw, lon_nw = num2deg(xtile, ytile, zoom)
        lat_se, lon_se = num2deg(xtile + 1, ytile + 1, zoom)

        width_km = haversine(lat, lon_nw, lat, lon_se)
        height_km = haversine(lat_nw, lon, lat_se, lon)

        if 3 <= width_km <= 8:
            return zoom
    return 13  # fallback

def download_heatmap_area(lat, lon, area_km=10, activity="run", output_path="heatmap_area.png"):
    zoom = get_appropriate_zoom(lat, lon)
    print(f"Zoom sélectionné : {zoom}")

    center_x, center_y = deg2num(lat, lon, zoom)
    tiles_needed = 2  # => 5x5 tuiles (environ 10 km)

    tile_size = 256
    total_width = tile_size * (2 * tiles_needed + 1)
    total_height = tile_size * (2 * tiles_needed + 1)
    combined_image = Image.new("RGBA", (total_width, total_height))

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for dx in range(-tiles_needed, tiles_needed + 1):
        for dy in range(-tiles_needed, tiles_needed + 1):
            x = center_x + dx
            y = center_y + dy
            url = f"https://strava-heatmap.tiles.freemap.sk/{activity}/hot/{zoom}/{x}/{y}.png"

            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                tile_image = Image.open(io.BytesIO(response.content))
                pos_x = (dx + tiles_needed) * tile_size
                pos_y = (dy + tiles_needed) * tile_size
                combined_image.paste(tile_image, (pos_x, pos_y))
                print(f"Téléchargé : {url}")
            except Exception as e:
                print(f"Erreur pour {url} : {e}")

    combined_image.save(output_path)
    print(f"Image sauvegardée : {output_path}")

# Exemple d'exécution en local
if __name__ == "__main__":
    download_heatmap_area(
        lat=43.48333,
        lon=3.66667,
        area_km=10,
        activity="run",
        output_path="strava_heatmap_10km_43.48333_3.66667.png"
    )
