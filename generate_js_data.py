import json

with open(r"d:\Escritorio\Data\peru_map_paths_exact.json", "r", encoding="utf-8") as f:
    data = json.load(f)

js_lines = ["const PERU_MAP_PATH_DATA = ["]
for item in data:
    js_lines.append(f'  {{ id: {item["id"]}, name: "{item["name"]}", region: "{item["region"]}", path: "{item["path"]}" }},')
js_lines.append("];")

js_code = "\n".join(js_lines)

with open(r"d:\Escritorio\Data\js_peru_map_path_data.js", "w", encoding="utf-8") as out:
    out.write(js_code)

print("Saved js_peru_map_path_data.js")
