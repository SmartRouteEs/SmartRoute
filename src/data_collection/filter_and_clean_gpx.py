import os
import math
import shutil
import glob
import xml.etree.ElementTree as ET
from geopy.distance import geodesic

# Dossiers
INPUT_DIR = "data/alternative_vtt_traces"
OUTPUT_DIR = "data/gpx_filtered2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Bounding box (lon_min, lat_min, lon_max, lat_max)
BBOX = [2.188650, 48.145309, 3.411287, 48.954693]

# Critères
MIN_POINTS = 4
MIN_DISTANCE_METERS = 3000  # 3 km
MAX_OUTSIDE_RATIO = 0.20    # 20% de points max hors zone

def is_point_in_bbox(lat, lon, bbox):
    return bbox[1] <= lat <= bbox[3] and bbox[0] <= lon <= bbox[2]

def compute_total_distance(coords):
    return sum(geodesic(coords[i - 1], coords[i]).meters for i in range(1, len(coords)))

def compute_bbox_area(bbox):
    lat_avg = (bbox[1] + bbox[3]) / 2
    km_per_deg_lon = 111.32 * math.cos(math.radians(lat_avg))
    km_per_deg_lat = 111.32
    return (bbox[2] - bbox[0]) * km_per_deg_lon * (bbox[3] - bbox[1]) * km_per_deg_lat

def filter_gpx_files():
    gpx_files = glob.glob(os.path.join(INPUT_DIR, "*.gpx"))
    print(f"🔍 {len(gpx_files)} fichiers trouvés dans {INPUT_DIR}")
    kept = 0

    for gpx_file in gpx_files:
        try:
            tree = ET.parse(gpx_file)
            root = tree.getroot()

            coords = []
            outside_count = 0

            for trkpt in root.findall(".//trkpt"):
                lat = float(trkpt.get("lat"))
                lon = float(trkpt.get("lon"))
                coords.append((lat, lon))
                if not is_point_in_bbox(lat, lon, BBOX):
                    outside_count += 1

            total_points = len(coords)
            if total_points < MIN_POINTS:
                continue

            outside_ratio = outside_count / total_points
            if outside_ratio > MAX_OUTSIDE_RATIO:
                continue

            total_distance = compute_total_distance(coords)
            if total_distance < MIN_DISTANCE_METERS:
                continue

            shutil.copy(gpx_file, OUTPUT_DIR)
            print(f"✅ Gardé : {os.path.basename(gpx_file)} - {total_points} points, {total_distance:.0f} m")
            kept += 1

        except Exception as e:
            print(f"❌ Erreur avec {os.path.basename(gpx_file)} : {e}")

    print(f"\n📦 {kept} traces valides copiées dans {OUTPUT_DIR}")

if __name__ == "__main__":
    print("🧹 FILTRAGE DES TRACES GPX")
    print("=" * 50)
    print(f"📍 Bounding Box : {BBOX}")
    area = compute_bbox_area(BBOX)
    print(f"📐 Surface estimée : {area:.1f} km²")
    print(f"📂 Lecture de {INPUT_DIR} et écriture dans {OUTPUT_DIR}...\n")
    filter_gpx_files()
