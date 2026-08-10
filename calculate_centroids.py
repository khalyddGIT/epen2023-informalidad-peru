import json, re

log_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\7d7045ae-dbee-4ee4-ae92-92ea9f05ac28\.system_generated\logs\transcript_full.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

line_240 = lines[240]

d_values = re.findall(r'd=\\"([^"\\]+)\\"', line_240)
print(f"Total d attributes: {len(d_values)}")

# Take the last 25 paths
dept_d_list = d_values[-25:]

paths_meta = []
for idx, d_str in enumerate(dept_d_list):
    # Extract numbers from path
    coords = [float(x) for x in re.findall(r'[-+]?\d*\.\d+|\d+', d_str)]
    xs = coords[0::2]
    ys = coords[1::2]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    paths_meta.append({
        "idx": idx,
        "cx": round(cx, 1),
        "cy": round(cy, 1),
        "min_x": round(min_x, 1),
        "max_x": round(max_x, 1),
        "min_y": round(min_y, 1),
        "max_y": round(max_y, 1),
        "d": d_str
    })

for item in paths_meta:
    print(f"Path {item['idx']}: cx={item['cx']}, cy={item['cy']}, bounds=({item['min_x']}..{item['max_x']}, {item['min_y']}..{item['max_y']})")

with open(r"d:\Escritorio\Data\paths_centroids.json", "w", encoding="utf-8") as out:
    json.dump(paths_meta, out, indent=2)
