from pathlib import Path

FOLDER = Path("data/gpx_clean")

def main():
    if not FOLDER.exists():
        print("📂 Dossier inexistant :", FOLDER)
        return

    files = list(FOLDER.glob("*.pkl"))
    if not files:
        print("✅ Dossier déjà vide.")
        return

    for file in files:
        file.unlink()
        print(f"🗑️ Supprimé : {file.name}")

    print(f"\n✅ {len(files)} fichier(s) supprimé(s) de {FOLDER}")

if __name__ == "__main__":
    main()
