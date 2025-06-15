from pathlib import Path
import pandas as pd
import numpy as np
import json

def load_trace_raw(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    legs = data.get("trip", {}).get("legs", [])
    trace_rows = []

    for leg in legs:
        for edge in leg.get("maneuvers", []):
            distance = edge.get("length", 0) * 1000  # km → m
            surface = edge.get("surface", "unknown").lower()
            dplus = edge.get("verbal_pre_transition_instruction", "").count("monter") * 5
            popularity = 49.0  # Valeur par défaut
            trace_rows.append({
                "trace_file": Path(path).name,
                "distance": distance,
                "dplus": dplus,
                "surface": surface,
                "popularity": popularity,
                "from_node": None,  # placeholders si pas fournis
                "to_node": None
            })

    return pd.DataFrame(trace_rows)

def enrich_trace_data(df):
    df["slope"] = df["dplus"] / (df["distance"] + 1e-6)
    df["log_distance"] = np.log1p(df["distance"])
    df["is_asphalt"] = (df["surface"] == "asphalt").astype(int)
    return df

def process_traces_to_dual_output(folder_path):
    all_segments = []
    for file in Path(folder_path).glob("*.json"):
        try:
            df = load_trace_raw(file)
            all_segments.append(df)
        except Exception as e:
            print(f"[ERREUR] Fichier {file.name} ignoré : {e}")

    if not all_segments:
        print("[ERREUR] Aucun fichier valide trouvé.")
        return pd.DataFrame(), pd.DataFrame()

    raw_df = pd.concat(all_segments, ignore_index=True)
    enriched_df = enrich_trace_data(raw_df.copy())
    return raw_df, enriched_df
