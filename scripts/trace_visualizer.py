import os
import glob
import folium
from xml.etree import ElementTree as ET
import random

def create_interactive_map(gpx_directory="osm_vtt_traces", num_traces=30):
    """
    Crée une carte interactive avec les traces VTT sur une vraie carte
    
    Args:
        gpx_directory: dossier contenant les fichiers GPX
        num_traces: nombre de traces à afficher
    """
    
    print(f"🗺️ CRÉATION D'UNE CARTE INTERACTIVE - {num_traces} TRACES")
    print("=" * 60)
    
    # Trouver les fichiers GPX
    gpx_files = glob.glob(os.path.join(gpx_directory, "*.gpx"))
    
    if not gpx_files:
        print(f"❌ Aucun fichier GPX trouvé dans {gpx_directory}")
        return
    
    print(f"📁 {len(gpx_files)} fichiers GPX disponibles")
    
    # Sélectionner aléatoirement quelques traces
    if len(gpx_files) > num_traces:
        selected_files = random.sample(gpx_files, num_traces)
    else:
        selected_files = gpx_files
    
    # Centre de la carte sur Fontainebleau
    fontainebleau_center = [48.4, 2.7]  # Coordonnées approximatives
    
    # Créer la carte avec différents fonds de carte
    m = folium.Map(
        location=fontainebleau_center,
        zoom_start=13,
        tiles='OpenStreetMap'
    )
    
    # Ajouter différents types de cartes (avec attributions correctes)
    folium.TileLayer(
        tiles='https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
        attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.',
        name='Terrain',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB positron',
        name='CartoDB Light',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
        name='Satellite',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Couleurs pour différencier les traces
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 
              'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 
              'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
    
    successful_traces = 0
    all_coords = []
    
    print(f"📊 Traitement de {len(selected_files)} traces...")
    
    for i, gpx_file in enumerate(selected_files):
        try:
            # Lire le fichier GPX
            tree = ET.parse(gpx_file)
            root = tree.getroot()
            
            # Extraire les coordonnées
            coords = []
            for trkpt in root.findall('.//trkpt'):
                lat = float(trkpt.get('lat'))
                lon = float(trkpt.get('lon'))
                coords.append([lat, lon])
            
            if len(coords) >= 2:
                # Couleur pour cette trace
                color = colors[i % len(colors)]
                
                # Nom de la trace
                trace_name = f"Trace {i+1}"
                filename = os.path.basename(gpx_file)
                
                # Ajouter la trace à la carte
                folium.PolyLine(
                    coords,
                    color=color,
                    weight=3,
                    opacity=0.8,
                    popup=f"{trace_name}\n{filename}\n{len(coords)} points"
                ).add_to(m)
                
                # Marqueur de début (vert)
                folium.Marker(
                    coords[0],
                    popup=f"🟢 Début {trace_name}",
                    icon=folium.Icon(color='green', icon='play')
                ).add_to(m)
                
                # Marqueur de fin (rouge)
                folium.Marker(
                    coords[-1],
                    popup=f"🔴 Fin {trace_name}",
                    icon=folium.Icon(color='red', icon='stop')
                ).add_to(m)
                
                # Collecter toutes les coordonnées pour ajuster la vue
                all_coords.extend(coords)
                
                successful_traces += 1
                print(f"   ✅ {trace_name}: {len(coords)} points ({filename})")
                
            else:
                print(f"   ⚠️ Trace {i+1}: trop peu de points")
                
        except Exception as e:
            print(f"   ❌ Erreur trace {i+1}: {e}")
    
    if successful_traces == 0:
        print("❌ Aucune trace n'a pu être ajoutée à la carte")
        return None
    
    # Ajuster la vue pour inclure toutes les traces
    if all_coords:
        # Calculer les limites
        lats = [coord[0] for coord in all_coords]
        lons = [coord[1] for coord in all_coords]
        
        # Centrer la carte sur toutes les traces
        sw = [min(lats), min(lons)]
        ne = [max(lats), max(lons)]
        m.fit_bounds([sw, ne])
    
    # Ajouter le contrôle des couches
    folium.LayerControl().add_to(m)
    
    # Ajouter une légende
    legend_html = f'''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 200px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>🚴 Traces VTT Fontainebleau</h4>
    <p>🟢 Début des traces</p>
    <p>🔴 Fin des traces</p>
    <p>📊 {successful_traces} traces affichées</p>
    <p>📍 Cliquez sur les lignes pour plus d'infos</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Sauvegarder la carte
    output_file = "fontainebleau_traces_map.html"
    m.save(output_file)
    
    print(f"\n🎯 CARTE INTERACTIVE CRÉÉE !")
    print(f"✅ {successful_traces} traces ajoutées")
    print(f"💾 Carte sauvegardée: {output_file}")
    print(f"🌐 Ouvrez le fichier dans votre navigateur pour voir la carte interactive")
    
    return output_file

def create_simple_web_map(gpx_directory="osm_vtt_traces", num_traces=3):
    """Version simplifiée qui fonctionne même sans folium"""
    
    print(f"🗺️ CRÉATION CARTE WEB SIMPLE - {num_traces} TRACES")
    print("=" * 50)
    
    # Vérifier les fichiers
    gpx_files = glob.glob(os.path.join(gpx_directory, "*.gpx"))
    
    if not gpx_files:
        print("❌ Aucun fichier GPX trouvé")
        return
    
    # Sélectionner quelques traces
    selected_files = gpx_files[:num_traces]
    
    # Extraire les coordonnées
    all_traces = []
    
    for i, gpx_file in enumerate(selected_files):
        try:
            tree = ET.parse(gpx_file)
            root = tree.getroot()
            
            coords = []
            for trkpt in root.findall('.//trkpt'):
                lat = float(trkpt.get('lat'))
                lon = float(trkpt.get('lon'))
                coords.append([lat, lon])
            
            if coords:
                all_traces.append({
                    'name': f'Trace {i+1}',
                    'coords': coords,
                    'file': os.path.basename(gpx_file)
                })
                
        except Exception as e:
            print(f"Erreur: {e}")
    
    if not all_traces:
        print("❌ Aucune trace valide")
        return
    
    # Créer HTML simple avec OpenStreetMap
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Traces VTT Fontainebleau</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <style>
            #map {{ height: 600px; width: 100%; }}
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
        </style>
    </head>
    <body>
        <h1>🚴 Traces VTT - Forêt de Fontainebleau</h1>
        <p>📊 {len(all_traces)} traces visualisées</p>
        <div id="map"></div>
        
        <script>
            // Centrer sur Fontainebleau
            var map = L.map('map').setView([48.4, 2.7], 13);
            
            // Ajouter la carte OpenStreetMap
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '© OpenStreetMap contributors'
            }}).addTo(map);
            
            // Couleurs pour les traces
            var colors = ['red', 'blue', 'green', 'purple', 'orange'];
            
    """
    
    # Ajouter chaque trace
    for i, trace in enumerate(all_traces):
        color = ['red', 'blue', 'green', 'purple', 'orange'][i % 5]
        
        html_content += f"""
            // Trace {i+1}: {trace['name']}
            var trace{i+1} = {trace['coords']};
            L.polyline(trace{i+1}, {{color: '{color}', weight: 3}})
                .addTo(map)
                .bindPopup("{trace['name']}<br>{trace['file']}<br>{len(trace['coords'])} points");
            
            // Marqueurs début/fin
            L.marker(trace{i+1}[0]).addTo(map)
                .bindPopup("🟢 Début {trace['name']}");
            L.marker(trace{i+1}[trace{i+1}.length-1]).addTo(map)
                .bindPopup("🔴 Fin {trace['name']}");
        """
    
    html_content += """
        </script>
    </body>
    </html>
    """
    
    # Sauvegarder
    output_file = "traces_map_simple.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Carte créée: {output_file}")
    print(f"🌐 Ouvrez ce fichier dans votre navigateur !")
    
    return output_file

# SCRIPT PRINCIPAL
if __name__ == "__main__":
    print("🗺️ VISUALISEUR DE TRACES SUR VRAIE CARTE")
    print("=" * 60)
    
    try:
        # Essayer d'installer folium si pas disponible
        import folium
        print("📦 Folium disponible - Création carte interactive avancée")
        map_file = create_interactive_map(num_traces=5)
        
    except ImportError:
        print("📦 Folium non disponible - Création carte web simple")
        print("💡 Pour une carte avancée: pip install folium")
        map_file = create_simple_web_map(num_traces=3)
    
    if map_file:
        print(f"\n🚀 INSTRUCTIONS:")
        print(f"1. Ouvrez votre navigateur web")
        print(f"2. Faites glisser le fichier '{map_file}' dans le navigateur")
        print(f"3. OU double-cliquez sur '{map_file}'")
        print(f"4. Explorez la carte interactive avec vos traces VTT !")
        
        print(f"\n🎯 FONCTIONNALITÉS DE LA CARTE:")
        print(f"- Zoom/déplacement avec la souris")
        print(f"- Clic sur les traces pour voir les détails")
        print(f"- Marqueurs verts = début, rouges = fin")
        print(f"- Différents fonds de carte disponibles")