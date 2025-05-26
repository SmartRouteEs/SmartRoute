import pickle
import matplotlib.pyplot as plt
from pathlib import Path
from shapely.geometry import LineString
import matplotlib.cm as cm
import matplotlib.colors as colors

GRAPH_PATH = Path("data/processed/graph_with_strava_and_dplus.gpickle")

def load_graph(path):
    with open(path, "rb") as f:
        return pickle.load(f)

def plot_dplus_colormap(G, min_dplus=0.0, max_edges=2000):
    edges = []
    dplus_values = []

    for u, v, k, d in G.edges(data=True, keys=True):
        dplus = d.get("dplus")
        geom = d.get("geometry")
        if isinstance(geom, LineString) and dplus is not None and dplus >= min_dplus:
            coords = list(geom.coords)
            lons, lats = zip(*coords)
            edges.append((lons, lats))
            dplus_values.append(dplus)
            if len(edges) >= max_edges:
                break

    if not edges:
        print("Aucune arête à afficher.")
        return

    norm = colors.Normalize(vmin=min(dplus_values), vmax=max(dplus_values))
    cmap = plt.get_cmap("viridis")

    fig, ax = plt.subplots(figsize=(10, 10))
    for (lons, lats), dplus in zip(edges, dplus_values):
        ax.plot(lons, lats, color=cmap(norm(dplus)), linewidth=1.5)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cbar = plt.colorbar(sm, ax=ax, orientation="vertical")
    cbar.set_label("D+ (m)")

    ax.set_title("Carte colorée des arêtes selon le D+")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    G = load_graph(GRAPH_PATH)
    plot_dplus_colormap(G, min_dplus=0.0, max_edges=2000)
