import json

# Exact mapping based on spatial coordinates:
exact_mapping = {
  0: {"id": 25, "name": "Ucayali", "region": "Selva"},
  1: {"id": 17, "name": "Madre de Dios", "region": "Selva"},
  2: {"id": 22, "name": "San Martin", "region": "Selva"},
  3: {"id": 1, "name": "Amazonas", "region": "Selva"},
  4: {"id": 16, "name": "Loreto", "region": "Selva"},
  5: {"id": 5, "name": "Ayacucho", "region": "Sierra"},
  6: {"id": 7, "name": "Callao", "region": "Costa"},
  7: {"id": 9, "name": "Huancavelica", "region": "Sierra"},
  8: {"id": 12, "name": "Junin", "region": "Sierra"},
  9: {"id": 15, "name": "Lima", "region": "Costa"},
  10: {"id": 14, "name": "Lambayeque", "region": "Costa"},
  11: {"id": 24, "name": "Tumbes", "region": "Costa"},
  12: {"id": 8, "name": "Cusco", "region": "Sierra"},
  13: {"id": 3, "name": "Apurimac", "region": "Sierra"},
  14: {"id": 21, "name": "Puno", "region": "Sierra"},
  15: {"id": 4, "name": "Arequipa", "region": "Costa"},
  16: {"id": 23, "name": "Tacna", "region": "Costa"},
  17: {"id": 2, "name": "Ancash", "region": "Sierra"},
  18: {"id": 6, "name": "Cajamarca", "region": "Sierra"},
  19: {"id": 10, "name": "Huanuco", "region": "Sierra"},
  20: {"id": 18, "name": "Moquegua", "region": "Costa"},
  21: {"id": 13, "name": "La Libertad", "region": "Costa"},
  22: {"id": 19, "name": "Pasco", "region": "Sierra"},
  23: {"id": 20, "name": "Piura", "region": "Costa"},
  24: {"id": 11, "name": "Ica", "region": "Costa"}
}

with open(r"d:\Escritorio\Data\paths_centroids.json", "r") as f:
    paths_meta = json.load(f)

result = []
for p in paths_meta:
    idx = p['idx']
    info = exact_mapping[idx]
    result.append({
        "id": info["id"],
        "name": info["name"],
        "region": info["region"],
        "path": p["d"]
    })

print(f"Mapped {len(result)} departments. Checking unique IDs:")
ids = [r["id"] for r in result]
names = [r["name"] for r in result]
print("Unique IDs count:", len(set(ids)))
print("Unique Names count:", len(set(names)))
if len(set(ids)) < 25:
    missing_ids = set(range(1, 26)) - set(ids)
    print("MISSING IDs:", missing_ids)

with open(r"d:\Escritorio\Data\peru_map_paths_exact.json", "w", encoding="utf-8") as out:
    json.dump(result, out, indent=2)

print("Saved to peru_map_paths_exact.json")
