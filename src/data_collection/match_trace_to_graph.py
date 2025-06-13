import os
import pickle
import requests
import json
import time
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2

# === CONFIGURATION ===
CLEAN_DIR = Path("data/gpx_clean")
OUT_DIR = Path("data/matched_traces")
VALHALLA_URL = "http://localhost:8002/trace_route"
COSTING = "bicycle"
CHUNK_SIZE = 400
OVERLAP = 50
INTERPOLATION_DISTANCE = 10
QUALITY_THRESHOLD = 0.7
BATCH_SIZE = 100  # <== Modifie ici pour adapter la taille du lot

OUT_DIR.mkdir(parents=True, exist_ok=True)

def haversine(coord1, coord2):
    R = 6371000
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def compute_distance(points):
    return sum(haversine(points[i], points[i+1]) for i in range(len(points)-1))

def send_valhalla_request(shape):
    body = {
        "shape": shape,
        "costing": COSTING,
        "shape_match": "map_snap",
        "trace_options": {
            "interpolation_distance": INTERPOLATION_DISTANCE
        }
    }
    try:
        res = requests.post(VALHALLA_URL, json=body)
        if res.status_code != 200:
            print(f"Erreur Valhalla: {res.status_code} - {res.text}")
            return None
        return res.json()
    except Exception as e:
        print("Erreur requête ou parsing:", e)
        return None

def extract_shape_points(data):
    if not data or "trip" not in data:
        return []
    points = []
    for leg in data["trip"]["legs"]:
        shape_raw = leg.get("shape", "")
        if isinstance(shape_raw, str):
            import polyline
            decoded = polyline.decode(shape_raw)
            points.extend(decoded)
        elif isinstance(shape_raw, list):
            points.extend(shape_raw)
    return points

def map_match_trace_full(trace_points):
    shape = [{"lat": lat, "lon": lon} for lat, lon in trace_points]
    if len(shape) <= CHUNK_SIZE:
        result = send_valhalla_request(shape)
        return [result] if result else [], trace_points

    chunks = []
    i = 0
    while i < len(shape):
        end = min(i + CHUNK_SIZE, len(shape))
        if end - i <= OVERLAP:
            break
        chunk = shape[i:end]
        result = send_valhalla_request(chunk)
        if result and "trip" in result:
            print(f"  - Bloc {i}-{end} : OK")
            chunks.append(result)
        else:
            print(f"  - Bloc {i}-{end} : échec")
        i = end - OVERLAP
    return chunks, trace_points

def estimate_coverage_by_distance(matched_chunks, original_points):
    matched_points = []
    for chunk in matched_chunks:
        matched_points.extend(extract_shape_points(chunk))
    dist_match = compute_distance(matched_points)
    dist_orig = compute_distance(original_points)
    if dist_orig == 0:
        return 0
    return dist_match / dist_orig

def merge_chunks(chunks):
    if not chunks:
        return None
    merged = {"trip": {"legs": []}}
    for chunk in chunks:
        if "trip" in chunk and "legs" in chunk["trip"]:
            merged["trip"]["legs"].extend(chunk["trip"]["legs"])
    return merged

def main():
    all_files = sorted(CLEAN_DIR.glob("*.pkl"))
    N = len(all_files)
    for batch_start in range(0, N, BATCH_SIZE):
        batch = all_files[batch_start:batch_start + BATCH_SIZE]
        print(f"\n=== Traitement du batch {batch_start//BATCH_SIZE+1} ({len(batch)} traces) ===")
        for file in batch:
            out_file = OUT_DIR / (file.stem + "_matched.json")
            if out_file.exists():
                print(f"{out_file.name} existe déjà, on saute cette trace.")
                continue

            print(f"\n=== Traitement de {file.name} ===")
            with open(file, "rb") as f:
                trace = pickle.load(f)

            matched_chunks, original_points = map_match_trace_full(trace)
            if not matched_chunks:
                print("✘ Matching échoué")
                time.sleep(1.0)
                continue

            coverage = estimate_coverage_by_distance(matched_chunks, original_points)
            if coverage < QUALITY_THRESHOLD:
                print(f"⚠️  Couverture faible (distance) : {coverage*100:.1f}%")
            else:
                print(f"✔ Bonne couverture (distance) : {coverage*100:.1f}%")

            result = merge_chunks(matched_chunks)
            with open(out_file, "w") as f:
                json.dump(result, f)
            print(f"Trace sauvegardée : {out_file}")
            time.sleep(1.0)  # Pause 1s après chaque trace

        print("\n=== Fin du batch ===")
        print("👉 Redémarre maintenant le serveur Docker Valhalla puis appuie sur Entrée pour continuer.")
        input("Appuie sur Entrée quand Valhalla est prêt...")

if __name__ == "__main__":
    main()
