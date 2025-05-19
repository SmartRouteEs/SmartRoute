from pathlib import Path
import os

CACHE_PATH = Path("data/cache/city_lookup.json")

def clear_cache():
    if CACHE_PATH.exists():
        os.remove(CACHE_PATH)
        print(f"🗑️ Cache supprimé : {CACHE_PATH}")
    else:
        print("✅ Aucun cache à supprimer.")

if __name__ == "__main__":
    clear_cache()

