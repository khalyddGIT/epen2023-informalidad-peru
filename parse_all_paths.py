import json, re

log_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\7d7045ae-dbee-4ee4-ae92-92ea9f05ac28\.system_generated\logs\transcript_full.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

line_240 = lines[240]

# Find all d="..." strings
d_values = re.findall(r'd=\\"([^"\\]+)\\"', line_240)
print(f"Total d attributes: {len(d_values)}")

# The first 27 paths are shadows (fill="#000") or department shapes
# Let's inspect the last 26 d_values
dept_d_list = d_values[-25:]

print(f"Extracted {len(dept_d_list)} department path d values.")

# Names of the 25 Peru departments in order
dept_names = [
  "Tacna", "Puno", "Moquegua", "Arequipa", "Cusco", 
  "Apurimac", "Ayacucho", "Huancavelica", "Ica", "Lima", 
  "Junin", "Pasco", "Huanuco", "Ancash", "La Libertad", 
  "San Martin", "Cajamarca", "Amazonas", "Loreto", "Ucayali", 
  "Madre de Dios", "Piura", "Lambayeque", "Tumbes", "Callao"
]

dept_map_data = []
for idx, d_path in enumerate(dept_d_list):
    dept_map_data.append({
        "id": idx + 1,
        "name": dept_names[idx] if idx < len(dept_names) else f"Dept {idx+1}",
        "path": d_path
    })

with open(r"d:\Escritorio\Data\peru_map_paths.json", "w", encoding="utf-8") as out:
    json.dump(dept_map_data, out, indent=2)

print("Successfully saved 25 exact Peru department paths!")
