import os
import pickle
import matplotlib.pyplot as plt
import gpxpy
import osmnx as ox
from shapely.geometry import LineString

# === Config ===
GRAPH_FILE = "data/processed/graph_wgs84.gpickle"
GPX_FILE = "data/gpx/vulaines-sur-seine.gpx"  # ← à adapter selon ta trace
ZOOM_PADDING = 0.01  # degrés (environ 1 km)

# === Chargement du graphe ===
print("> Chargement du graphe...")
with open(GRAPH_FILE, "rb") as f:
    G = pickle.load(f)

# === Chargement de la trace GPX ===
print(f"> Lecture de la trace GPX : {GPX_FILE}")
with open(GPX_FILE, "r") as gpx_file:
    gpx = gpxpy.parse(gpx_file)

# === Extraction des points GPS
points = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            points.append((point.longitude, point.latitude))

if len(points) < 2:
    print("⚠️ Pas assez de points dans la trace.")
    exit()

trace_line = LineString(points)

# === Déterminer la bounding box de la trace
minx, miny, maxx, maxy = trace_line.bounds
bbox = (miny - ZOOM_PADDING, maxy + ZOOM_PADDING, minx - ZOOM_PADDING, maxx + ZOOM_PADDING)

# === Filtrage du graphe local
print("> Filtrage local du graphe pour la visualisation...")
G_sub = G.subgraph([
    n for n, data in G.nodes(data=True)
    if bbox[0] <= data["y"] <= bbox[1] and bbox[2] <= data["x"] <= bbox[3]
])

# === Tracé
fig, ax = ox.plot_graph(G_sub, show=False, close=False, node_size=0, edge_color="lightgray", edge_linewidth=0.6)

# Ajout de la trace GPX
xs, ys = zip(*points)
ax.plot(xs, ys, color='red', linewidth=2, label="Trace GPX")

plt.title(f"Trace GPX brute : {os.path.basename(GPX_FILE)}")
plt.legend()
plt.tight_layout()
plt.show()
