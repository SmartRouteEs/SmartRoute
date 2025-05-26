import subprocess
from pathlib import Path

# Dossier contenant les .asc (dans les sous-dossiers)
asc_root = Path("data/dem")
# Dossier où placer les .tif convertis
tif_output = Path("data/dem/tif")
tif_output.mkdir(parents=True, exist_ok=True)

# Recherche de tous les .asc
asc_files = list(asc_root.rglob("*.asc"))
print(f"📦 {len(asc_files)} fichiers .asc trouvés")

for asc in asc_files:
    tif = tif_output / (asc.stem + ".tif")
    print(f"🔄 Conversion : {asc.name} → {tif.name}")
    subprocess.run(["gdal_translate", "-of", "GTiff", str(asc), str(tif)])

print("✅ Conversion terminée : tous les .asc → .tif dans data/dem/tif")
