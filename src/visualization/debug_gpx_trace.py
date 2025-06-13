import gpxpy
from pathlib import Path
from simplification.cutil import simplify_coords_vw
import matplotlib.pyplot as plt
import math

# === CONFIGURATION ===
GPX_FILE = Path("data/gpx/vulaines-sur-seine.gpx")
EPSILON = 5.0  # seuil de simplification (m)

def haversine(coord1, coord2):
    from math import radians, sin, cos, sqrt, atan2
    R = 6371000
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def clean_trace(points, min_spacing=2.0):
    cleaned = [points[0]]
    for pt in points[1:]:
        if haversine(pt, cleaned[-1]) > min_spacing:
            cleaned.append(pt)
    return cleaned

def main():
    with open(GPX_FILE, "r") as f:
        gpx = gpxpy.parse(f)

    points = [
        (pt.latitude, pt.longitude)
        for track in gpx.tracks
        for segment in track.segments
        for pt in segment.points
    ]

    print(f"> {GPX_FILE.name} :")
    print(f"  - Points bruts : {len(points)}")

    cleaned = clean_trace(points)
    print(f"  - Points nettoyés : {len(cleaned)}")

    simplified = simplify_coords_vw([(lon, lat) for lat, lon in cleaned], EPSILON)
    simplified = [(lat, lon) for lon, lat in simplified]
    print(f"  - Points simplifiés : {len(simplified)}")

    total_dist = sum(haversine(simplified[i], simplified[i+1]) for i in range(len(simplified)-1))
    print(f"  - Distance totale : {total_dist / 1000:.2f} km")

    # === VISUALISATION ===
    lats_raw, lons_raw = zip(*points)
    lats_clean, lons_clean = zip(*cleaned)
    lats_simp, lons_simp = zip(*simplified)

    plt.figure(figsize=(8, 6))
    plt.plot(lons_raw, lats_raw, 'gray', alpha=0.4, label="Brut")
    plt.plot(lons_clean, lats_clean, 'blue', alpha=0.6, label="Nettoyé")
    plt.plot(lons_simp, lats_simp, 'red', linewidth=2, label="Simplifié")
    plt.title(f"Trace : {GPX_FILE.name}")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.axis("equal")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
