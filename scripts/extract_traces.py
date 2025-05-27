import requests
import json
import os
import time
from datetime import datetime

# 🎯 SOLUTION 1: OPENSTREETMAP + OVERPASS API (RECOMMANDÉE)
# ============================================================================

def get_vtt_trails_from_osm(bbox, output_dir="osm_vtt_traces"):
    """
    Récupère les sentiers VTT depuis OpenStreetMap via Overpass API
    
    Args:
        bbox: [lon_min, lat_min, lon_max, lat_max]
        output_dir: dossier de sortie
    
    Returns:
        dict avec les données récupérées
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Requête Overpass pour les sentiers VTT dans votre zone
    overpass_query = f"""
    [out:json][timeout:120];
    (
      // Sentiers VTT spécifiquement balisés
      way["route"="mtb"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      way["mtb"="yes"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      way["bicycle"="yes"]["surface"~"dirt|earth|gravel|sand"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      
      // Chemins forestiers et ruraux
      way["highway"="track"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      way["highway"="path"]["bicycle"="yes"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      way["highway"="path"]["mtb"="yes"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      
      // Sentiers de randonnée autorisés au VTT
      way["highway"="path"]["surface"~"dirt|earth|gravel|sand"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      way["highway"="bridleway"]["bicycle"="yes"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      
      // Relations de parcours VTT
      relation["type"="route"]["route"="mtb"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
    );
    out geom;
    """
    
    print("🔍 Récupération des sentiers VTT depuis OpenStreetMap...")
    print(f"📍 Zone: {bbox[2]-bbox[0]:.3f}° x {bbox[3]-bbox[1]:.3f}° (~{((bbox[2]-bbox[0]) * (bbox[3]-bbox[1]) * 111 * 111):.0f} km²)")
    
    # Envoi de la requête à l'API Overpass
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    try:
        response = requests.post(overpass_url, data=overpass_query, timeout=120)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"✅ {len(data['elements'])} éléments trouvés")
        
        # Convertir en traces GPX
        gpx_files = convert_osm_to_gpx(data, output_dir)
        
        # Sauvegarder les données brutes
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
    """Convertit les données OSM en fichiers GPX"""
    
    gpx_files = []
    
    for i, element in enumerate(osm_data['elements']):
        if element['type'] == 'way' and 'geometry' in element:
            
            # Extraire les métadonnées
            tags = element.get('tags', {})
            name = tags.get('name', f"Sentier VTT {i+1}")
            surface = tags.get('surface', 'unknown')
            difficulty = tags.get('mtb:scale', 'unknown')
            highway_type = tags.get('highway', 'unknown')
            
            # Créer le contenu GPX
            gpx_content = create_gpx_from_geometry(
                element['geometry'], 
                name, 
                surface, 
                difficulty,
                highway_type
            )
            
            # Sauvegarder le fichier
            filename = f"osm_trail_{element['id']}.gpx"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(gpx_content)
            
            gpx_files.append(filepath)
    
    return gpx_files

def create_gpx_from_geometry(geometry, name, surface, difficulty, highway_type):
    """Crée un fichier GPX à partir de la géométrie OSM"""
    
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
    
    # Ajouter les points de la trace
    track_points = ""
    for point in geometry:
        track_points += f'        <trkpt lat="{point["lat"]}" lon="{point["lon"]}"></trkpt>\n'
    
    return gpx_header + "\n" + track_points + gpx_footer

# ============================================================================
# FONCTIONS D'ANALYSE POUR GRANDE ZONE
# ============================================================================

def analyze_trail_distribution(results, bbox):
    """Analyse la distribution des sentiers dans la zone"""
    
    if 'error' in results or not results['gpx_files']:
        return
    
    print(f"\n📊 ANALYSE DE LA DISTRIBUTION DES SENTIERS")
    print("=" * 50)
    
    # Calculer la densité
    area_km2 = ((bbox[2]-bbox[0]) * (bbox[3]-bbox[1]) * 111 * 111)
    density = results['total_elements'] / area_km2
    
    print(f"🗺️  Surface totale: {area_km2:.1f} km²")
    print(f"🚵 Sentiers trouvés: {results['total_elements']}")
    print(f"📈 Densité: {density:.2f} sentiers/km²")
    
    # Recommandations selon la taille de zone
    if area_km2 > 2000:
        print(f"\n⚠️  ZONE TRÈS ÉTENDUE DÉTECTÉE")
        print("💡 Recommandations:")
        print("   - Considérer diviser en sous-zones")
        print("   - Traitement par chunks recommandé")
        print("   - Temps d'extraction potentiellement long")

def split_large_bbox(bbox, max_area_km2=500):
    """Divise une grande bbox en plus petites zones"""
    
    area_km2 = ((bbox[2]-bbox[0]) * (bbox[3]-bbox[1]) * 111 * 111)
    
    if area_km2 <= max_area_km2:
        return [bbox]
    
    # Calculer le nombre de divisions nécessaires
    divisions = int((area_km2 / max_area_km2) ** 0.5) + 1
    
    lon_step = (bbox[2] - bbox[0]) / divisions
    lat_step = (bbox[3] - bbox[1]) / divisions
    
    sub_bboxes = []
    
    for i in range(divisions):
        for j in range(divisions):
            sub_bbox = [
                bbox[0] + i * lon_step,      # lon_min
                bbox[1] + j * lat_step,      # lat_min
                bbox[0] + (i + 1) * lon_step, # lon_max
                bbox[1] + (j + 1) * lat_step  # lat_max
            ]
            sub_bboxes.append(sub_bbox)
    
    print(f"🔄 Zone divisée en {len(sub_bboxes)} sous-zones de ~{max_area_km2} km² chacune")
    return sub_bboxes

# ============================================================================
# PARTIE PRINCIPALE - EXÉCUTION DU SCRIPT
# ============================================================================

if __name__ == "__main__":
    print("🚴 EXTRACTEUR DE TRACES VTT - NOUVELLE ZONE")
    print("=" * 60)
    
    # ✨ VOTRE NOUVELLE ZONE DE TRAVAIL ✨
    # Conversion de: E 2°32'00"--E 3°17'00"/N 48°53'00"--N 48°23'00"
    nouvelle_zone_bbox = [2.533333, 48.383333, 3.283333, 48.883333]
    
    print(f"📍 Zone d'extraction: Votre zone personnalisée")
    print(f"🗺️  Coordonnées: {nouvelle_zone_bbox}")
    print(f"📏 Taille zone: {nouvelle_zone_bbox[2]-nouvelle_zone_bbox[0]:.3f}° x {nouvelle_zone_bbox[3]-nouvelle_zone_bbox[1]:.3f}°")
    print(f"📐 Superficie: ~{((nouvelle_zone_bbox[2]-nouvelle_zone_bbox[0]) * (nouvelle_zone_bbox[3]-nouvelle_zone_bbox[1]) * 111 * 111):.0f} km²")
    
    # Vérifier si la zone est très grande
    area_km2 = ((nouvelle_zone_bbox[2]-nouvelle_zone_bbox[0]) * (nouvelle_zone_bbox[3]-nouvelle_zone_bbox[1]) * 111 * 111)
    
    if area_km2 > 1000:
        print(f"\n⚠️  ZONE ÉTENDUE DÉTECTÉE ({area_km2:.0f} km²)")
        print("💭 Options disponibles:")
        print("   1. Extraction complète (peut prendre du temps)")
        print("   2. Division en sous-zones (recommandé)")
        
        # Pour cet exemple, on continue avec l'extraction complète
        # Vous pouvez décommenter la ligne suivante pour diviser:
        # sub_bboxes = split_large_bbox(nouvelle_zone_bbox)
    
    # Lancement de l'extraction
    print("\n🚀 Démarrage de l'extraction...")
    print("⏳ Patience, zone étendue en cours de traitement...")
    
    results = get_vtt_trails_from_osm(nouvelle_zone_bbox)
    
    # Affichage des résultats
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS DE L'EXTRACTION")
    print("=" * 60)
    
    if 'error' in results:
        print(f"❌ Erreur: {results['error']}")
        print("\n💡 Solutions possibles:")
        print("- Vérifier votre connexion internet")
        print("- Réessayer dans quelques minutes")
        print("- L'API Overpass peut être temporairement surchargée")
        print("- Pour une zone si étendue, essayer de diviser en sous-zones")
    else:
        print(f"✅ Source: {results['source']}")
        print(f"📍 Éléments OSM trouvés: {results['total_elements']}")
        print(f"📁 Fichiers GPX créés: {len(results['gpx_files'])}")
        print(f"💾 Données brutes: {results['raw_data_file']}")
        
        # Analyse détaillée
        analyze_trail_distribution(results, nouvelle_zone_bbox)
        
        print(f"\n📂 FICHIERS GÉNÉRÉS:")
        print(f"   Dossier: osm_vtt_traces/")
        
        if results['gpx_files']:
            print(f"   📄 {len(results['gpx_files'])} fichiers .gpx")
            print(f"   📋 1 fichier osm_raw_data.json")
            
            # Afficher quelques exemples de fichiers
            print(f"\n🔍 EXEMPLES DE FICHIERS:")
            for i, gpx_file in enumerate(results['gpx_files'][:5]):  # 5 premiers
                print(f"   {i+1}. {os.path.basename(gpx_file)}")
            
            if len(results['gpx_files']) > 5:
                print(f"   ... et {len(results['gpx_files'])-5} autres fichiers")
        
        print(f"\n🎯 UTILISATION POUR VOTRE IA:")
        print("   - Fichiers GPX prêts pour l'entraînement")
        print("   - Métadonnées incluses (surface, difficulté, type)")
        print("   - Géométrie complète des sentiers")
        print("   - Format standard compatible avec tous les outils")
        print("   - Zone étendue = dataset plus riche")
        
        print(f"\n✨ EXTRACTION TERMINÉE AVEC SUCCÈS!")
        
        # Statistiques détaillées
        if results['total_elements'] > 0:
            print(f"\n📈 STATISTIQUES DÉTAILLÉES:")
            print(f"   🗺️  Zone analysée: {area_km2:.1f} km²")
            print(f"   🚵 Sentiers par km²: {results['total_elements'] / area_km2:.2f}")
            print(f"   📊 Richesse du dataset: {'Excellent' if results['total_elements'] > 1000 else 'Bon' if results['total_elements'] > 100 else 'Modéré'}")