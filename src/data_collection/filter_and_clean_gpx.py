import os
import gpxpy
import pickle
from pathlib import Path
from typing import List, Tuple
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime

# === PARAMÈTRES ===
MIN_DISTANCE = 10000            # Distance minimale (en mètres)
MIN_POINTS = 10                 # Nombre de points minimum
MAX_POINTS_ALLOWED = 3000       # Pour éviter des traces trop longues
MAX_SPEED_KMH = 59              # Seuil de vitesse maximum
PRECISION = 5                   # Pour le hash de doublons

# Bounding box du graphe enrichi
MIN_LON, MAX_LON = 2.188650, 3.411287
MIN_LAT, MAX_LAT = 48.145309, 48.954693

INPUT_DIR = Path("data/gpx/")
OUTPUT_DIR = Path("data/gpx_clean/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
seen_traces = set()

def haversine(coord1, coord2):
    R = 6371000
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def interpolate_points(p1, p2, t1, t2, max_dist=20):
    dist = haversine(p1, p2)
    if dist <= max_dist:
        return [p1]
    n_points = int(dist // max_dist) + 1
    points = []
    for i in range(n_points):
        frac = i / n_points
        lat = p1[0] + frac * (p2[0] - p1[0])
        lon = p1[1] + frac * (p2[1] - p1[1])
        points.append((lat, lon))
    return points

def clean_trace(points: List[Tuple[Tuple[float, float], datetime]]) -> List[Tuple[float, float]]:
    cleaned = []
    for i, (pt, time) in enumerate(points):
        if not cleaned:
            cleaned.append((pt, time))
            continue
        dist = haversine(cleaned[-1][0], pt)
        if time and cleaned[-1][1]:
            dt = (time - cleaned[-1][1]).total_seconds()
            speed = dist / dt * 3.6 if dt > 0 else 0
            if speed > MAX_SPEED_KMH:
                continue
        if dist > 2.0:
            cleaned.append((pt, time))

    interpolated = []
    for i in range(len(cleaned) - 1):
        interpolated.extend(interpolate_points(
            cleaned[i][0], cleaned[i+1][0],
            cleaned[i][1], cleaned[i+1][1]
        ))
    if cleaned:
        interpolated.append(cleaned[-1][0])
    return interpolated

def get_trace_id(trace: List[Tuple[float, float]], precision=5) -> int:
    rounded = [(round(lat, precision), round(lon, precision)) for lat, lon in trace]
    return hash(tuple(rounded))

def is_within_bounding_box(trace: List[Tuple[float, float]]) -> bool:
    for lat, lon in trace:
        if not (MIN_LAT <= lat <= MAX_LAT and MIN_LON <= lon <= MAX_LON):
            return False
    return True

def process_gpx_file(filepath: Path):
    try:
        with open(filepath, 'r') as f:
            gpx = gpxpy.parse(f)
    except Exception as e:
        print(f"Erreur lecture {filepath.name}: {e}")
        return None

    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for pt in segment.points:
                points.append(((pt.latitude, pt.longitude), pt.time))

    if len(points) < MIN_POINTS:
        print(f"✗ {filepath.name} ignorée (trop peu de points bruts)")
        return None

    total_dist_before = sum(haversine(points[i][0], points[i+1][0]) for i in range(len(points)-1))
    print(f"> {filepath.name} : {len(points)} points bruts, distance approx {total_dist_before/1000:.2f} km")

    cleaned = clean_trace(points)

    if len(cleaned) < MIN_POINTS:
        print(f"✗ {filepath.name} ignorée (trop peu de points nettoyés)")
        return None

    if len(cleaned) > MAX_POINTS_ALLOWED:
        print(f"✗ {filepath.name} ignorée (trop de points après interpolation : {len(cleaned)})")
        return None

    if not is_within_bounding_box(cleaned):
        print(f"✗ {filepath.name} ignorée (hors de la bounding box)")
        return None

    total_dist = sum(haversine(cleaned[i], cleaned[i+1]) for i in range(len(cleaned)-1))
    if total_dist < MIN_DISTANCE:
        print(f"✗ {filepath.name} ignorée ({total_dist/1000:.2f} km après nettoyage)")
        return None

    trace_id = get_trace_id(cleaned, precision=PRECISION)
    if trace_id in seen_traces:
        print(f"✗ {filepath.name} ignorée (doublon détecté)")
        return None
    seen_traces.add(trace_id)

    print(f"✓ {filepath.name} : {total_dist/1000:.2f} km, {len(cleaned)} points gardés")
    return cleaned

def main():
    files = list(INPUT_DIR.glob("*.gpx"))
    print(f"> Traitement de {len(files)} fichiers GPX...")

    for fpath in files:
        result = process_gpx_file(fpath)
        if result is not None:
            out_name = fpath.stem + ".pkl"
            out_path = OUTPUT_DIR / out_name
            with open(out_path, "wb") as out_f:
                pickle.dump(result, out_f)

if __name__ == "__main__":
    main()
