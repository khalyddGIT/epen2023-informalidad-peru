import json, re

log_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\7d7045ae-dbee-4ee4-ae92-92ea9f05ac28\.system_generated\logs\transcript_full.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

user_svg_text = ""
for line in reversed(lines):
    if 'rompiste el frontend' in line or 'mejora la parte de la mapa' in line or 'baseProfile="full"' in line:
        user_svg_text = line
        break

print("Found line length:", len(user_svg_text))

# Search for <path d="..."
# Note: in json string, quotes might be escaped \"
paths_d = re.findall(r'd=\\?"([^"\\]+)\\?"', user_svg_text)
print("Paths d found:", len(paths_d))

fills = re.findall(r'fill=\\?"([^"\\]+)\\?"', user_svg_text)
print("Fills found:", len(fills))

# Combine d and fill
dept_list = []
for i in range(min(len(paths_d), len(fills))):
    fill_val = fills[i]
    if fill_val != '#000':
        dept_list.append({"index": len(dept_list) + 1, "fill": fill_val, "path": paths_d[i]})

print(f"Filtered real colored paths: {len(dept_list)}")

with open(r"d:\Escritorio\Data\real_peru_svg_paths.json", "w", encoding="utf-8") as out:
    json.dump(dept_list, out, indent=2)

print("Saved to real_peru_svg_paths.json")
