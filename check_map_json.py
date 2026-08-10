import json

with open(r"d:\Escritorio\Data\frontend\src\peru_map_paths.json", "r") as f:
    map_paths = json.load(f)

# Backend IDs from database query:
# id: 1: Amazonas, 2: Ancash, 3: Apurimac, 4: Arequipa, 5: Ayacucho, 6: Cajamarca, 7: Callao (or missing), 8: Cusco, 9: Huancavelica, 10: Huanuco, 11: Ica, 12: Junin, 13: La Libertad, 14: Lambayeque, 15: Lima, 16: Loreto, 17: Madre de Dios, 18: Moquegua, 19: Pasco, 20: Piura, 21: Puno, 22: San Martin, 23: Tacna, 24: Tumbes, 25: Ucayali

print("Comparing peru_map_paths.json items:")
for p in map_paths:
    print(f"id: {p['id']:2d} | name: {p['name']:15s} | path length: {len(p['path'])}")

