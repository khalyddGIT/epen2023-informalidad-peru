import json, re

log_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\7d7045ae-dbee-4ee4-ae92-92ea9f05ac28\.system_generated\logs\transcript_full.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

line_240 = lines[240]
all_d = re.findall(r'd=\\"([^"\\]+)\\"', line_240)

# Filter out path 22 (len 101, island) and path 0 (duplicate Ica shadow path)
# Let's inspect all 27 paths and match each department:

paths_dict = {}
for idx, d_str in enumerate(all_d):
    coords = [float(x) for x in re.findall(r'[-+]?\d*\.\d+|\d+', d_str)]
    if not coords:
        continue
    xs = coords[0::2]
    ys = coords[1::2]
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    paths_dict[idx] = {
        "idx": idx,
        "len": len(d_str),
        "cx": round(cx, 1),
        "cy": round(cy, 1),
        "min_x": round(min(xs), 1),
        "max_x": round(max(xs), 1),
        "min_y": round(min(ys), 1),
        "max_y": round(max(ys), 1),
        "d": d_str
    }

# Department Mappings by exact coordinates:
# 1. Loreto: Path 6 (cx=429.8, cy=149.6)
# 2. Tumbes: Path 13 (cx=273.5, cy=141.6)
# 3. Piura: Path 25 (cx=279.6, cy=172.4)
# 4. Lambayeque: Path 12 (cx=294.6, cy=199.8)
# 5. Cajamarca: Path 20 (cx=314.1, cy=201.0)
# 6. Amazonas: Path 5 (cx=332.5, cy=170.8)
# 7. San Martin: Path 4 (cx=362.5, cy=215.0)
# 8. La Libertad: Path 23 (cx=326.4, cy=235.3)
# 9. Ancash: Path 19 (cx=338.8, cy=272.3)
# 10. Huanuco: Path 21 (cx=377.4, cy=268.9)
# 11. Ucayali: Path 2 (cx=435.2, cy=272.4)
# 12. Pasco: Path 24 (cx=389.8, cy=294.9)
# 13. Junin: Path 10 (cx=402.4, cy=321.9)
# 14. Lima: Path 11 (cx=362.0, cy=321.6)
# 15. Callao: Path 8 (cx=358.2, cy=331.0)
# 16. Huancavelica: Path 9 (cx=402.0, cy=354.8)
# 17. Ica: Path 26 (cx=388.0, cy=380.7)
# 18. Ayacucho: Path 7 (cx=422.1, cy=377.0)
# 19. Apurimac: Path 14 (cx=444.7, cy=380.2)
# 20. Cusco: Path 1 (cx=466.7, cy=362.7)  <--- THIS WAS MISSING!
# 21. Madre de Dios: Path 3 (cx=494.3, cy=329.3)
# 22. Puno: Path 16 (cx=515.9, cy=409.7)
# 23. Arequipa: Path 15 (cx=454.2, cy=418.0)
# 24. Moquegua: Path 17 (cx=492.8, cy=445.8)
# 25. Tacna: Path 18 (cx=503.8, cy=460.8)

dept_mappings = [
    { "id": 16, "name": "Loreto", "region": "Selva", "path_idx": 6 },
    { "id": 24, "name": "Tumbes", "region": "Costa", "path_idx": 13 },
    { "id": 20, "name": "Piura", "region": "Costa", "path_idx": 25 },
    { "id": 14, "name": "Lambayeque", "region": "Costa", "path_idx": 12 },
    { "id": 6,  "name": "Cajamarca", "region": "Sierra", "path_idx": 20 },
    { "id": 1,  "name": "Amazonas", "region": "Selva", "path_idx": 5 },
    { "id": 22, "name": "San Martin", "region": "Selva", "path_idx": 4 },
    { "id": 13, "name": "La Libertad", "region": "Costa", "path_idx": 23 },
    { "id": 2,  "name": "Ancash", "region": "Sierra", "path_idx": 19 },
    { "id": 10, "name": "Huanuco", "region": "Sierra", "path_idx": 21 },
    { "id": 25, "name": "Ucayali", "region": "Selva", "path_idx": 2 },
    { "id": 19, "name": "Pasco", "region": "Sierra", "path_idx": 24 },
    { "id": 12, "name": "Junin", "region": "Sierra", "path_idx": 10 },
    { "id": 15, "name": "Lima", "region": "Costa", "path_idx": 11 },
    { "id": 7,  "name": "Callao", "region": "Costa", "path_idx": 8 },
    { "id": 9,  "name": "Huancavelica", "region": "Sierra", "path_idx": 9 },
    { "id": 11, "name": "Ica", "region": "Costa", "path_idx": 26 },
    { "id": 5,  "name": "Ayacucho", "region": "Sierra", "path_idx": 7 },
    { "id": 3,  "name": "Apurimac", "region": "Sierra", "path_idx": 14 },
    { "id": 8,  "name": "Cusco", "region": "Sierra", "path_idx": 1 },
    { "id": 17, "name": "Madre de Dios", "region": "Selva", "path_idx": 3 },
    { "id": 21, "name": "Puno", "region": "Sierra", "path_idx": 16 },
    { "id": 4,  "name": "Arequipa", "region": "Costa", "path_idx": 15 },
    { "id": 18, "name": "Moquegua", "region": "Costa", "path_idx": 17 },
    { "id": 23, "name": "Tacna", "region": "Costa", "path_idx": 18 },
]

print("Checking uniqueness of 25 mapped departments:")
ids = [d["id"] for d in dept_mappings]
names = [d["name"] for d in dept_mappings]
idxs = [d["path_idx"] for d in dept_mappings]

print("Unique IDs count:", len(set(ids)))
print("Unique Names count:", len(set(names)))
print("Unique Path Indices count:", len(set(idxs)))

final_peru_paths = []
for d in dept_mappings:
    p_info = paths_dict[d["path_idx"]]
    final_peru_paths.append({
        "id": d["id"],
        "name": d["name"],
        "region": d["region"],
        "path": p_info["d"]
    })

with open(r"d:\Escritorio\Data\frontend\src\peru_map_paths.json", "w", encoding="utf-8") as out:
    json.dump(final_peru_paths, out, indent=2)

print("SUCCESSFULLY WRITTEN FULL 25 DEPARTMENTS TO peru_map_paths.json!")
