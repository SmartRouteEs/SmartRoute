import os
import glob
import folium
from xml.etree import ElementTree as ET
import random

def create_interactive_map(gpx_directory="data/gpx", num_traces=30):
    print(f"🗺️ CRÉATION D'UNE CARTE INTERACTIVE - {num_traces} TRACES")
    print("=" * 60)
    
    gpx_files = glob.glob(os.path.join(gpx_directory, "*.gpx"))
    if not gpx_files:
        print(f"❌ Aucun fichier GPX trouvé dans {gpx_directory}")
        return

    print(f"📁 {len(gpx_files)} fichiers GPX disponibles")

    selected_files = random.sample(gpx_files, min(num_traces, len(gpx_files)))
    center = [48.4, 2.7]
    m = folium.Map(location=center, zoom_start=13, tiles='OpenStreetMap')

    folium.TileLayer(
        tiles='https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
        attr='Stamen Design | OpenStreetMap',
        name='Terrain', control=True
    ).add_to(m)

    folium.TileLayer('CartoDB positron', name='CartoDB Light', control=True).add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri | USGS | OpenStreetMap',
        name='Satellite', control=True
    ).add_to(m)

    colors = ['red', 'blue', 'green', 'purple', 'orange', 'black', 'gray']
    successful_traces, all_coords = 0, []

    for i, gpx_file in enumerate(selected_files):
        try:
            tree = ET.parse(gpx_file)
            root = tree.getroot()
            coords = [[float(pt.get('lat')), float(pt.get('lon'))] for pt in root.findall('.//trkpt')]

            if len(coords) >= 2:
                color = colors[i % len(colors)]
                name = f"Trace {i+1}"
                folium.PolyLine(coords, color=color, weight=3, opacity=0.8,
                                popup=f"{name}\n{os.path.basename(gpx_file)}").add_to(m)
                folium.Marker(coords[0], popup=f"🟢 Début {name}", icon=folium.Icon(color='green')).add_to(m)
                folium.Marker(coords[-1], popup=f"🔴 Fin {name}", icon=folium.Icon(color='red')).add_to(m)
                all_coords.extend(coords)
                successful_traces += 1
        except Exception as e:
            print(f"❌ Erreur lecture {gpx_file} : {e}")

    if all_coords:
        lats, lons = zip(*all_coords)
        m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])

    folium.LayerControl().add_to(m)

    legend = f"""
    <div style="position: fixed; top: 10px; right: 10px; width: 200px; background-color: white;
                border:2px solid grey; z-index:9999; font-size:14px; padding: 10px">
    <h4>🚴 Traces VTT</h4>
    <p>🟢 Début</p><p>🔴 Fin</p><p>📊 {successful_traces} traces affichées</p>
    </div>"""
    m.get_root().html.add_child(folium.Element(legend))

    output_file = "carte_traces_vtt.html"
    m.save(output_file)
    print(f"\n✅ Carte créée : {output_file}")
    return output_file

def create_simple_web_map(gpx_directory="data/gpx", num_traces=3):
    print("🗺️ CRÉATION CARTE WEB SIMPLE")
    gpx_files = glob.glob(os.path.join(gpx_directory, "*.gpx"))
    if not gpx_files:
        print("❌ Aucun fichier GPX trouvé")
        return

    selected_files = gpx_files[:num_traces]
    all_traces = []

    for i, gpx_file in enumerate(selected_files):
        try:
            tree = ET.parse(gpx_file)
            coords = [[float(pt.get('lat')), float(pt.get('lon'))] for pt in tree.getroot().findall('.//trkpt')]
            if coords:
                all_traces.append({'name': f'Trace {i+1}', 'coords': coords, 'file': os.path.basename(gpx_file)})
        except Exception as e:
            print(f"Erreur : {e}")

    if not all_traces:
        return

    html = f"""
    <!DOCTYPE html><html><head>
        <title>Traces VTT</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        <style>#map {{ height: 600px; }}</style>
    </head><body>
    <h1>Traces VTT</h1><div id="map"></div><script>
    var map = L.map('map').setView([48.4, 2.7], 13);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
    """

    for i, trace in enumerate(all_traces):
        color = ['red', 'blue', 'green', 'purple', 'orange'][i % 5]
        html += f"""
        var trace{i} = {trace['coords']};
        L.polyline(trace{i}, {{color: '{color}', weight: 3}}).addTo(map)
            .bindPopup("{trace['name']}<br>{trace['file']}");
        L.marker(trace{i}[0]).addTo(map).bindPopup("Début {trace['name']}");
        L.marker(trace{i}[trace{i}.length - 1]).addTo(map).bindPopup("Fin {trace['name']}");
        """

    html += "</script></body></html>"

    output_file = "traces_map_simple.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Carte simple créée : {output_file}")
    return output_file

# SCRIPT PRINCIPAL
if __name__ == "__main__":
    print("🗺️ VISUALISATION DE TRACES GPX DEPUIS data/gpx")
    try:
        import folium
        map_file = create_interactive_map(gpx_directory="data/gpx", num_traces=5)
    except ImportError:
        map_file = create_simple_web_map(gpx_directory="data/gpx", num_traces=3)

    if map_file:
        print(f"\n🌐 Ouvrez '{map_file}' dans votre navigateur pour voir la carte.")
