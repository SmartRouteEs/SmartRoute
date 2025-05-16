import math

def deg2num(lat_deg, lon_deg, zoom):
    """Convertit des coordonnées latitude/longitude en coordonnées de tuiles x/y pour un niveau de zoom donné."""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile

def num2deg(xtile, ytile, zoom):
    """Renvoie la latitude/longitude du coin nord-ouest d'une tuile x/y."""
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg

def haversine(lat1, lon1, lat2, lon2):
    """Calcule la distance entre deux points en km."""
    R = 6371  # Rayon moyen de la Terre en km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_zoom_for_area(area_km, max_tiles=100, lat=45.0):
    """
    Trouve dynamiquement le niveau de zoom pour couvrir area_km × area_km
    sans dépasser max_tiles au total (par exemple 100 tuiles).
    """
    for zoom in reversed(range(10, 16)):  # du zoom le + précis au + large
        # Approx. taille d'une tuile à cette latitude
        tile_km = 40075 * math.cos(math.radians(lat)) / (2 ** zoom)
        nb_tiles = (area_km / tile_km) ** 2
        if nb_tiles <= max_tiles:
            return zoom
    return 12  # fallback large si tout échoue


