import requests
import json
import os
import time
import math
from datetime import datetime

def get_vtt_trails_from_osm(bbox, output_dir="data/gpx"):
    """
    Récupère les sentiers VTT depuis OpenStreetMap via Overpass API
    Args:
        bbox: [lon_min, lat_min, lon_max, lat_max]
        output_dir: dossier de sortie
    Returns:
        dict avec les données récupérées
    """
    os.makedirs(output_dir, exist_ok=True)

    # Calcul de surface précise en km²
    lat_avg = (bbox[1] + bbox[3]) / 2
    km_per_deg_lat = 111.32
    km_per_deg_lon = 111.32 * math.cos(math.radians(lat_avg))
    lat_km = (bbox[3] - bbox[1]) * km_per_deg_lat
    lon_km = (bbox[2] - bbox[0]) * km_per_deg_lon
    area_km2 = lat_km * lon_km

    print("🔍 Récupération des sentiers VTT depuis OpenStreetMap...")
    print(f"📍 Zone: {lat_km:.1f} km x {lon_km:.1f} km ≈ {area_km2:.0f} km²")

    overpass_query = f"""
    [out:json][timeout:120];
    (
      way["route"="mtb"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      way["mtb"="yes"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      way["bicycle"="yes"]["surface"~"dirt|earth|gravel|sand"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      way["highway"="track"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      way["highway"="path"]["bicycle"="yes"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      way["highway"="path"]["mtb"="yes"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      way["highway"="path"]["surface"~"dirt|earth|gravel|sand"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      way["highway"="bridleway"]["bicycle"="yes"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      relation["type"="route"]["route"="mtb"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
    );
    out geom;
    """

    try:
        response = requests.post("https://overpass-api.de/api/interpreter", data=overpass_query, timeout=120)
        response.raise_for_status()
        data = response.json()

        print(f"✅ {len(data['elements'])} éléments trouvés")

        gpx_files = convert_osm_to_gpx(data, output_dir)

        raw_file = os.path.join(output_dir, "osm_raw_data.json")
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return {
            'source': 'OpenStreetMap',
            'total_elements': len(data['elements']),
            'gpx_files': gpx_files,
            'raw_data_file': raw_file
        }

    except Exception as e:
        print(f"❌ Erreur OSM: {e}")
        return {'error': str(e)}

def convert_osm_to_gpx(osm_data, output_dir):
    gpx_files = []
    for i, element in enumerate(osm_data['elements']):
        if element['type'] == 'way' and 'geometry' in element:
            tags = element.get('tags', {})
            name = tags.get('name', f"Sentier VTT {i+1}")
            surface = tags.get('surface', 'unknown')
            difficulty = tags.get('mtb:scale', 'unknown')
            highway_type = tags.get('highway', 'unknown')

            gpx_content = create_gpx_from_geometry(
                element['geometry'], name, surface, difficulty, highway_type
            )

            filename = f"osm_trail_{element['id']}.gpx"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(gpx_content)

            gpx_files.append(filepath)
    return gpx_files

def create_gpx_from_geometry(geometry, name, surface, difficulty, highway_type):
    gpx_header = '''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="OSM-VTT-Extractor">
<metadata>
    <name>{name}</name>
    <desc>Sentier VTT - Type: {highway_type} - Surface: {surface} - Difficulté: {difficulty}</desc>
    <time>{time}</time>
</metadata>
<trk>
    <name>{name}</name>
    <type>mtb</type>
    <trkseg>'''.format(
        name=name,
        highway_type=highway_type,
        surface=surface,
        difficulty=difficulty,
        time=datetime.now().isoformat()
    )

    gpx_footer = '''    </trkseg>
</trk>
</gpx>'''

    track_points = "\n".join(
        f'        <trkpt lat="{point["lat"]}" lon="{point["lon"]}"></trkpt>'
        for point in geometry
    )

    return gpx_header + "\n" + track_points + "\n" + gpx_footer

# ============================================================================
if __name__ == "__main__":
    print("🚴 EXTRACTEUR DE TRACES VTT - ZONE CORRIGÉE")
    nouvelle_zone_bbox = [2.188650, 48.145309, 3.411287, 48.954693]

    results = get_vtt_trails_from_osm(nouvelle_zone_bbox, output_dir="data/gpx")

    print("\n📊 RÉSULTATS DE L'EXTRACTION")
    if 'error' in results:
        print(f"❌ Erreur: {results['error']}")
    else:
        print(f"✅ Source: {results['source']}")
        print(f"📍 Éléments OSM trouvés: {results['total_elements']}")
        print(f"📁 Fichiers GPX créés: {len(results['gpx_files'])}")
        print(f"💾 Données brutes: {results['raw_data_file']}")
        print(f"📂 Fichiers enregistrés dans: data/gpx/")
