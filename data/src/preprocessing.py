import pandas as pd
import geopandas as gpd
import os

# --- Chargement du fichier .parquet ---
print("Chargement du fichier...")
gdf = gpd.read_parquet("data/raw/data.parquet")

# --- Extraction des points GPS de chaque trajet ---
print("Extraction des coordonnées...")
rows = []
for trajet_id, row in gdf.iterrows():
    line = row.geometry
    if line is not None:
        for i, (lon, lat) in enumerate(line.coords):
            rows.append({
                "trajet_id": trajet_id,
                "index_in_trajet": i,
                "latitude": lat,
                "longitude": lon
            })

df_traces = pd.DataFrame(rows)
print(f"Total de points extraits : {len(df_traces)}")

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
output_path = "data/processed/clean_traces.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df_traces.to_csv("data/processed/clean_traces.csv.gz", compression='gzip', index=False)

print(f"Données sauvegardées dans : {output_path}")
