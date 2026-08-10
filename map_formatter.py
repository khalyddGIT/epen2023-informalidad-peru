import json

with open(r"d:\Escritorio\Data\peru_map_paths.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ID mapping to match our backend IdDepartamento:
# 1: Amazonas, 2: Ancash, 3: Apurimac, 4: Arequipa, 5: Ayacucho, 6: Cajamarca, 7: Callao, 8: Cusco, 9: Huancavelica, 10: Huanuco, 11: Ica, 12: Junin, 13: La Libertad, 14: Lambayeque, 15: Lima, 16: Loreto, 17: Madre de Dios, 18: Moquegua, 19: Pasco, 20: Piura, 21: Puno, 22: San Martin, 23: Tacna, 24: Tumbes, 25: Ucayali

name_to_id = {
  "Amazonas": 1, "Ancash": 2, "Apurimac": 3, "Arequipa": 4, "Ayacucho": 5, "Cajamarca": 6, "Callao": 7,
  "Cusco": 8, "Huancavelica": 9, "Huanuco": 10, "Ica": 11, "Junin": 12, "La Libertad": 13, "Lambayeque": 14,
  "Lima": 15, "Loreto": 16, "Madre de Dios": 17, "Moquegua": 18, "Pasco": 19, "Piura": 20, "Puno": 21,
  "San Martin": 22, "Tacna": 23, "Tumbes": 24, "Ucayali": 25
}

name_to_region = {
  "Amazonas": "Selva", "Ancash": "Sierra", "Apurimac": "Sierra", "Arequipa": "Costa", "Ayacucho": "Sierra",
  "Cajamarca": "Sierra", "Callao": "Costa", "Cusco": "Sierra", "Huancavelica": "Sierra", "Huanuco": "Sierra",
  "Ica": "Costa", "Junin": "Sierra", "La Libertad": "Costa", "Lambayeque": "Costa", "Lima": "Costa",
  "Loreto": "Selva", "Madre de Dios": "Selva", "Moquegua": "Costa", "Pasco": "Sierra", "Piura": "Costa",
  "Puno": "Sierra", "San Martin": "Selva", "Tacna": "Costa", "Tumbes": "Costa", "Ucayali": "Selva"
}

formatted_paths = []
for item in data:
    name = item["name"]
    dept_id = name_to_id.get(name, item["id"])
    region = name_to_region.get(name, "Costa")
    formatted_paths.append({
        "id": dept_id,
        "name": name,
        "region": region,
        "path": item["path"]
    })

print(f"Formatted {len(formatted_paths)} paths.")
with open(r"d:\Escritorio\Data\peru_map_paths_formatted.json", "w", encoding="utf-8") as out:
    json.dump(formatted_paths, out, indent=2)
