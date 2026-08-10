import json

with open(r"d:\Escritorio\Data\paths_centroids.json", "r") as f:
    paths = json.load(f)

# Correct Mapping from Path Index -> INEI Department:
correct_map = [
    { "id": 25, "name": "Ucayali", "region": "Selva", "path_idx": 0 },
    { "id": 17, "name": "Madre de Dios", "region": "Selva", "path_idx": 1 },
    { "id": 22, "name": "San Martin", "region": "Selva", "path_idx": 2 },
    { "id": 1, "name": "Amazonas", "region": "Selva", "path_idx": 3 },
    { "id": 16, "name": "Loreto", "region": "Selva", "path_idx": 4 },
    { "id": 5, "name": "Ayacucho", "region": "Sierra", "path_idx": 5 },
    { "id": 7, "name": "Callao", "region": "Costa", "path_idx": 6 },
    { "id": 9, "name": "Huancavelica", "region": "Sierra", "path_idx": 7 },
    { "id": 12, "name": "Junin", "region": "Sierra", "path_idx": 8 },
    { "id": 15, "name": "Lima", "region": "Costa", "path_idx": 9 },
    { "id": 14, "name": "Lambayeque", "region": "Costa", "path_idx": 10 },
    { "id": 24, "name": "Tumbes", "region": "Costa", "path_idx": 11 },
    { "id": 8, "name": "Cusco", "region": "Sierra", "path_idx": 12 },
    { "id": 3, "name": "Apurimac", "region": "Sierra", "path_idx": 13 },
    { "id": 21, "name": "Puno", "region": "Sierra", "path_idx": 14 },
    { "id": 18, "name": "Moquegua", "region": "Costa", "path_idx": 15 },
    { "id": 23, "name": "Tacna", "region": "Costa", "path_idx": 16 },
    { "id": 2, "name": "Ancash", "region": "Sierra", "path_idx": 17 },
    { "id": 6, "name": "Cajamarca", "region": "Sierra", "path_idx": 18 },
    { "id": 10, "name": "Huanuco", "region": "Sierra", "path_idx": 19 },
    { "id": 4, "name": "Arequipa", "region": "Costa", "path_idx": 13 },  # Arequipa / Apurimac southern vector
    { "id": 13, "name": "La Libertad", "region": "Costa", "path_idx": 21 },
    { "id": 19, "name": "Pasco", "region": "Sierra", "path_idx": 22 },
    { "id": 20, "name": "Piura", "region": "Costa", "path_idx": 23 },
    { "id": 11, "name": "Ica", "region": "Costa", "path_idx": 24 }
]

final_json = []
for item in correct_map:
    idx = item["path_idx"]
    final_json.append({
        "id": item["id"],
        "name": item["name"],
        "region": item["region"],
        "path": paths[idx]["d"]
    })

print(f"Generated {len(final_json)} entries for peru_map_paths.json.")
ids = [x["id"] for x in final_json]
print("Unique IDs count:", len(set(ids)))

with open(r"d:\Escritorio\Data\frontend\src\peru_map_paths.json", "w", encoding="utf-8") as out:
    json.dump(final_json, out, indent=2)

print("Saved updated peru_map_paths.json")
