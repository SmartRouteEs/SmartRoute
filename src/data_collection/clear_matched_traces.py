import os
from pathlib import Path

def clean_matched_traces_folder(folder_path="data/matched_traces"):
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Le dossier {folder_path} n'existe pas.")
        return
    
    files = list(folder.glob("*"))
    if not files:
        print(f"Aucun fichier à supprimer dans {folder_path}.")
        return

    for file in files:
        try:
            if file.is_file():
                file.unlink()
                print(f"Supprimé : {file.name}")
        except Exception as e:
            print(f"Erreur lors de la suppression de {file.name} : {e}")

    print(f"Nettoyage terminé du dossier {folder_path}.")

if __name__ == "__main__":
    clean_matched_traces_folder()
