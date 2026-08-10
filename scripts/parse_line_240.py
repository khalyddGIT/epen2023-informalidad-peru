import json, re

log_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\7d7045ae-dbee-4ee4-ae92-92ea9f05ac28\.system_generated\logs\transcript_full.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

line_240 = lines[240]

# Find all path strings in line 240
# Format: <path d="..." ... fill="..." ...>
path_matches = re.findall(r'<path d=\\"([^"\\]+)\\"[^>]*fill=\\"([^"\\]+)\\"', line_240)
print(f"Path matches found: {len(path_matches)}")

# Filter paths where fill is not #000 (shadows)
colored_paths = [p for p in path_matches if p[1] != '#000']
print(f"Colored department paths: {len(colored_paths)}")

out_list = []
for idx, (d, fill) in enumerate(colored_paths):
    out_list.append({
        "id": idx + 1,
        "fill": fill,
        "path": d
    })

with open(r"d:\Escritorio\Data\real_peru_paths.json", "w", encoding="utf-8") as out:
    json.dump(out_list, out, indent=2)

print("Saved 25 department paths to real_peru_paths.json!")
