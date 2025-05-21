with_geom = 0
without_geom = 0

for _, _, _, data in G.edges(keys=True, data=True):
    if isinstance(data.get("geometry"), LineString):
        with_geom += 1
    else:
        without_geom += 1

print("✅ Avec géométrie :", with_geom)
print("⛔️ Sans géométrie :", without_geom)
