import pandas as pd
import geopandas as gpd
import os

# --- Chargement du fichier .parquet ---
print("Chargement du fichier...")
gdf = gpd.read_parquet("data/raw/data.parquet")  # Assurez-vous que ce fichier contient bien des géométries

# Vérification de la structure du GeoDataFrame
print(gdf.columns)  # Affiche les colonnes pour vérifier qu'il y a bien une colonne 'geometry'

# --- Extraction des points GPS de chaque trajet ---
print("Extraction des coordonnées...")
rows = []

# Vérifie si la colonne 'geometry' existe et contient des géométries valides
if 'geometry' in gdf.columns:
    for trajet_id, row in gdf.iterrows():
        line = row.geometry
        if line is not None:
            # Assumer qu'on a un LINESTRING (un trajet)
            for i, (lon, lat) in enumerate(line.coords):
                rows.append({
                    "trajet_id": trajet_id,
                    "index_in_trajet": i,
                    "latitude": lat,
                    "longitude": lon
                })

    df_traces = pd.DataFrame(rows)
    print(f"Total de points extraits : {len(df_traces)}")
else:
    print("Erreur : Pas de géométries trouvées dans le fichier.")

# --- Nettoyage des données ---
print("Nettoyage des données...")

# Supprimer les valeurs manquantes
df_traces.dropna(inplace=True)

# Supprimer les points GPS aberrants (hors du monde réel)
df_traces = df_traces[
    (df_traces['latitude'].between(-90, 90)) &
    (df_traces['longitude'].between(-180, 180))
]

# Supprimer les trajets trop courts (< 10 points)
trajet_counts = df_traces['trajet_id'].value_counts()
trajets_valides = trajet_counts[trajet_counts >= 10].index
df_traces = df_traces[df_traces['trajet_id'].isin(trajets_valides)]

print(f"Nombre de trajets conservés : {df_traces['trajet_id'].nunique()}")
print(f"Nombre total de points après nettoyage : {len(df_traces)}")

# --- Sauvegarde du résultat ---
output_path = "data/processed/clean_traces.parquet"  # On garde le fichier en format Parquet
os.makedirs(os.path.dirname(output_path), exist_ok=True)

df_traces.to_parquet(output_path, compression='snappy', index=False)

print(df_traces.head())  # Affiche les premières lignes du DataFrame pour vérification
print(f"Données sauvegardées dans : {output_path}")
