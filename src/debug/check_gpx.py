import pickle
from pathlib import Path
from math import radians, cos, sin, asin, sqrt

CLEAN_DIR = Path("data/gpx_clean")

def haversine(lon1, lat1, lon2, lat2):
    # Calcul de la distance entre 2 points GPS en mètres
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371000  # rayon Terre en m
    return c * r

def analyze_trace(points):
    total_distance = 0.0
    distances = []
    for i in range(1, len(points)):
        dist = haversine(points[i-1][1], points[i-1][0], points[i][1], points[i][0])
        distances.append(dist)
        total_distance += dist
    avg_distance = sum(distances)/len(distances) if distances else 0
    return total_distance, avg_distance

def main():
    for file_path in CLEAN_DIR.glob("*.pkl"):
        with open(file_path, "rb") as f:
            points = pickle.load(f)
        if not points:
            print(f"{file_path.name} est vide")
            continue
        total_dist, avg_dist = analyze_trace(points)
        print(f"Trace {file_path.name}:")
        print(f"  Nombre de points : {len(points)}")
        print(f"  Distance totale approximative : {total_dist/1000:.2f} km")
        print(f"  Distance moyenne entre points : {avg_dist:.1f} m\n")

if __name__ == "__main__":
    main()
