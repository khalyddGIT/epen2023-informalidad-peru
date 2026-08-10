import json

with open(r"d:\Escritorio\Data\paths_centroids.json", "r") as f:
    paths = json.load(f)

# Map each path index 0..24 to a department:
path_assignments = {
    0:  {"id": 25, "name": "Ucayali", "region": "Selva"},
    1:  {"id": 17, "name": "Madre de Dios", "region": "Selva"},
    2:  {"id": 22, "name": "San Martin", "region": "Selva"},
    3:  {"id": 1,  "name": "Amazonas", "region": "Selva"},
    4:  {"id": 16, "name": "Loreto", "region": "Selva"},
    5:  {"id": 5,  "name": "Ayacucho", "region": "Sierra"},
    6:  {"id": 7,  "name": "Callao", "region": "Costa"},
    7:  {"id": 9,  "name": "Huancavelica", "region": "Sierra"},
    8:  {"id": 12, "name": "Junin", "region": "Sierra"},
    9:  {"id": 15, "name": "Lima", "region": "Costa"},
    10: {"id": 14, "name": "Lambayeque", "region": "Costa"},
    11: {"id": 24, "name": "Tumbes", "region": "Costa"},
    12: {"id": 8,  "name": "Cusco", "region": "Sierra"},
    13: {".id": 4,  "name": "Arequipa", "region": "Costa"},  # Arequipa / Apurimac
    14: {"id": 21, "name": "Puno", "region": "Sierra"},
    15: {"id": 18, "name": "Moquegua", "region": "Costa"},
    16: {"id": 23, "name": "Tacna", "region": "Costa"},
    17: {"id": 2,  "name": "Ancash", "region": "Sierra"},
    18: {"id": 6,  "name": "Cajamarca", "region": "Sierra"},
    19: {"id": 10, "name": "Huanuco", "region": "Sierra"},
    20: {"id": 3,  "name": "Apurimac", "region": "Sierra"}, # Or Callao island
    21: {"id": 13, "name": "La Libertad", "region": "Costa"},
    22: {"id": 19, "name": "Pasco", "region": "Sierra"},
    23: {"id": 20, "name": "Piura", "region": "Costa"},
    24: {"id": 11, "name": "Ica", "region": "Costa"}
}

# Let's build 25 objects for peru_map_paths.json:
peru_map_paths = []
for idx in range(25):
    meta = path_assignments[idx]
    # If key starts with dot, fix it
    id_val = meta.get("id") or meta.get(".id")
    peru_map_paths.append({
        "id": id_val,
        "name": meta["name"],
        "region": meta["region"],
        "path": paths[idx]["d"]
    })

with open(r"d:\Escritorio\Data\frontend\src\peru_map_paths.json", "w", encoding="utf-8") as out:
    json.dump(peru_map_paths, out, indent=2)

print("Updated peru_map_paths.json with all 25 distinct paths!")
