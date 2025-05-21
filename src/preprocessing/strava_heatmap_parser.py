# src/preprocessing/strava_heatmap_parser.py

import rasterio
from shapely.geometry import LineString
import numpy as np
import networkx as nx

class StravaHeatmapProcessor:
    """
    Classe utilitaire pour extraire les intensités Strava à partir d'une heatmap raster
    et les projeter sur les arêtes d'un graphe OSM.
    """

    def __init__(self, heatmap_path):
        """
        Initialise le processeur avec le chemin vers la heatmap.
        """
        self.heatmap_path = heatmap_path
        self.dataset = rasterio.open(heatmap_path)

    def get_intensity_at_point(self, lon, lat):
        """
        Récupère la valeur de la heatmap à une coordonnée (lon, lat).
        """
        try:
            row, col = self.dataset.index(lon, lat)
            return self.dataset.read(1)[row, col]
        except IndexError:
            return 0  # Valeur nulle si le point est hors image

    def compute_edge_intensity(self, edge_geometry, n_points=10):
        """
        Moyenne de l'intensité Strava le long d'une arête.
        """
        points = [
            edge_geometry.interpolate(dist, normalized=True)
            for dist in np.linspace(0, 1, num=n_points)
        ]
        intensities = [
            self.get_intensity_at_point(p.x, p.y)
            for p in points
        ]
        return np.mean(intensities) if intensities else 0

    def enrich_graph(self, G, geometry_key="geometry", output_key="strava"):
        """
        Ajoute un attribut d'intensité Strava à chaque arête du graphe G.
        """
        for u, v, data in G.edges(data=True):
            geom = data.get(geometry_key)
            if isinstance(geom, LineString):
                intensity = self.compute_edge_intensity(geom)
                data[output_key] = intensity
            else:
                data[output_key] = 0  # Si pas de géométrie, valeur par défaut
        return G
