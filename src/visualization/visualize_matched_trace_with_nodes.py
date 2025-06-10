import os
import pickle
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox

# === Config ===
GRAPH_FILE = "data/processed/graph_wgs84.gpickle"
MATCHED_TRACE_FILE = "data/processed/matched_traces/fontainebleau.pkl"  # change ce nom
ZOOM_PADDING = 0.01  # pour ajuster le zoom autour de la trace

# === Chargement ===
print("> Chargement du graphe...")
with open(GRAPH_FILE, "rb") as f:
    G = pickle.load(f)

print("> Chargement des arêtes matched...")
with open(MATCHED_TRACE_FILE, "rb") as f:
    matched_edges = pickle.load(f)

if not matched_edges:
    print("⚠️ Aucune arête matched.")
    exit()

# === Création d’un sous-graphe localisé sur les arêtes matched ===
nodes_in_trace = set()
for u, v, k in matched_edges:
    nodes_in_trace.add(u)
    nodes_in_trace.add(v)

subgraph_nodes = G.subgraph(nodes_in_trace).copy()
matched_subgraph = G.edge_subgraph(matched_edges).copy()

# === Définir la bounding box de zoom
lons = [G.nodes[n]['x'] for n in nodes_in_trace]
lats = [G.nodes[n]['y'] for n in nodes_in_trace]
minx, maxx = min(lons) - ZOOM_PADDING, max(lons) + ZOOM_PADDING
miny, maxy = min(lats) - ZOOM_PADDING, max(lats) + ZOOM_PADDING

# === Tracer
fig, ax = plt.subplots(figsize=(10, 10))

# Graphe complet en fond (optionnel)
ox.plot_graph(G, ax=ax, show=False, close=False, node_size=0, edge_color="lightgray", edge_linewidth=0.5)

# Arêtes matched
for u, v, k in matched_edges:
    data = G.get_edge_data(u, v, k)
    if "geometry" in data:
        xs, ys = data["geometry"].xy
    else:
        xs = [G.nodes[u]["x"], G.nodes[v]["x"]]
        ys = [G.nodes[u]["y"], G.nodes[v]["y"]]
    ax.plot(xs, ys, color="red", linewidth=2)

# Nœuds matched
node_x = [G.nodes[n]['x'] for n in nodes_in_trace]
node_y = [G.nodes[n]['y'] for n in nodes_in_trace]
ax.scatter(node_x, node_y, color='blue', s=10, label="nœuds matched")

# Zoom + titre
ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy)
ax.set_title(f"Arêtes + nœuds matched : {os.path.basename(MATCHED_TRACE_FILE)}")
ax.legend()
plt.tight_layout()
plt.show()
