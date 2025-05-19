import pandas as pd
from pathlib import Path

# === Fichiers d'entrée
CODES_CSV = Path("data/raw/019HexaSmal.csv")
POP_CSV = Path("data/raw/donnees_communes.csv")
OUTPUT_CSV = Path("data/processed/postal_population.csv")

# === Étape 1 : Charger le fichier La Poste (codes postaux)
df_codes = pd.read_csv(CODES_CSV, sep=";", dtype=str, encoding="latin1")

# Nettoyer les noms de colonnes
df_codes.columns = df_codes.columns.str.strip().str.replace("#", "")  # enlever le '#' de '#Code_commune_INSEE'

# Corriger le nom des colonnes et leur contenu
df_codes["Code_postal"] = df_codes["Code_postal"].str.zfill(5)
df_codes = df_codes.rename(columns={"Code_commune_INSEE": "code_commune_INSEE"})

# === Étape 2 : Charger les populations INSEE
df_pop = pd.read_csv(POP_CSV, sep=";", dtype=str, encoding="utf-8")
df_pop["code_commune_INSEE"] = df_pop["CODDEP"] + df_pop["CODCOM"].str.zfill(3)
df_pop["population"] = df_pop["PTOT"].astype(int)
df_pop = df_pop[["code_commune_INSEE", "population"]]

# === Étape 3 : Associer via code INSEE
df_merge = df_codes.merge(df_pop, on="code_commune_INSEE", how="left")

# === Étape 4 : Nettoyage et export
df_final = df_merge[["Code_postal", "population"]].dropna().drop_duplicates()
df_final["population"] = df_final["population"].astype(int)
df_final = df_final.rename(columns={"Code_postal": "postal_code"})
df_final = df_final.sort_values("postal_code")

# Créer dossier si besoin et sauvegarder
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
df_final.to_csv(OUTPUT_CSV, index=False)

print(f"✅ postal_population.csv généré avec {len(df_final)} codes postaux.")
