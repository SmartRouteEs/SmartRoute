import osmnx as ox
import os

# Utiliser un serveur alternatif si le principal échoue
ox.settings.overpass_endpoint = "https://overpass.kumi.systems/api/interpreter"


def download_osm_graph(lat, lon, dist_km=25, mode="bike"):
    """
    Télécharge (ou charge en cache) un graphe OSM centré sur (lat, lon)
    avec un rayon dist_km (en kilomètres).
    """
    filename = f"osm_graph_{mode}_{dist_km}km_{round(lat, 3)}_{round(lon, 3)}.graphml"
    filepath = os.path.join("data", "raw_osm", filename)

    if os.path.exists(filepath):
        print(f"✅ Chargement depuis le cache : {filepath}")
        G = ox.load_graphml(filepath)
    else:
        print("📡 Téléchargement depuis OpenStreetMap...")
        dist_m = dist_km * 1000
        G = ox.graph_from_point((lat, lon), dist=dist_m, network_type=mode, simplify=True)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        ox.save_graphml(G, filepath)
        print(f"💾 Graphe OSM sauvegardé : {filepath}")

    return G


if __name__ == "__main__":
    # Centre de la zone (même que Strava)
    lat = 48.55
    lon = 2.8
    G = download_osm_graph(lat, lon, dist_km=45, mode="bike")

    fig, ax = ox.plot_graph(
    G,
    bgcolor="white",
    node_color="black",
    edge_color="blue",
    edge_linewidth=0.8,
    show=False,
    close=True
)

fig.savefig("data/raw_osm/osm_graph_45km.png", dpi=300)
print("🖼️ Image sauvegardée : data/raw_osm/osm_graph_45km.png")




