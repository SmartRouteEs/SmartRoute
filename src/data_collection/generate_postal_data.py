import pandas as pd
from pathlib import Path

# === Fichiers d'entrée
CODES_CSV = Path("data/raw/019HexaSmal.csv")
POP_CSV = Path("data/raw/donnees_communes.csv")
GRID_CSV = Path("data/raw/postal_grid.csv")
OUTPUT_CSV = Path("data/processed/postal_population.csv")

# === Charger les données
df_codes = pd.read_csv(CODES_CSV, sep=";", dtype=str, encoding="latin1")
df_codes.columns = df_codes.columns.str.strip().str.replace("#", "")
df_codes = df_codes.rename(columns={"Code_commune_INSEE": "code_commune_INSEE"})
df_codes["Code_postal"] = df_codes["Code_postal"].str.zfill(5)

df_pop = pd.read_csv(POP_CSV, sep=";", dtype=str, encoding="utf-8")
df_pop["code_commune_INSEE"] = df_pop["CODDEP"] + df_pop["CODCOM"].str.zfill(3)
df_pop["population"] = df_pop["PTOT"].astype(int)

# === Lier INSEE ↔ Code postal ↔ Population
df = df_codes.merge(df_pop, on="code_commune_INSEE", how="left")
df = df[["Code_postal", "population"]].dropna()
df["population"] = df["population"].astype(int)

# === Filtrer selon grille
df_grid = pd.read_csv(GRID_CSV)
codes_utilisés = set(df_grid["postal_code"].astype(str).str.zfill(5))
df = df[df["Code_postal"].isin(codes_utilisés)]

# === Sauvegarde
df = df.rename(columns={"Code_postal": "postal_code"})
df = df.groupby("postal_code", as_index=False)["population"].sum()
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_CSV, index=False)

print(f"✅ postal_population.csv généré avec {len(df)} codes postaux.")
