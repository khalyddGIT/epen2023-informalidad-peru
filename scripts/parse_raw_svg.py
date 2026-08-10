import json, re

log_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\7d7045ae-dbee-4ee4-ae92-92ea9f05ac28\.system_generated\logs\transcript_full.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

line_240 = lines[240]

# Extract all d="..." in line 240
all_d = re.findall(r'd=\\"([^"\\]+)\\"', line_240)
print(f"Total d attributes in user prompt SVG: {len(all_d)}")

all_paths_meta = []
for idx, d_str in enumerate(all_d):
    coords = [float(x) for x in re.findall(r'[-+]?\d*\.\d+|\d+', d_str)]
    if not coords:
        continue
    xs = coords[0::2]
    ys = coords[1::2]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    all_paths_meta.append({
        "idx": idx,
        "len": len(d_str),
        "cx": round(cx, 1),
        "cy": round(cy, 1),
        "min_x": round(min_x, 1),
        "max_x": round(max_x, 1),
        "min_y": round(min_y, 1),
        "max_y": round(max_y, 1),
        "d": d_str
    })

for item in all_paths_meta:
    print(f"Path {item['idx']:2d}: len={item['len']:4d} | cx={item['cx']:5.1f}, cy={item['cy']:5.1f} | X: {item['min_x']:5.1f}..{item['max_x']:5.1f} | Y: {item['min_y']:5.1f}..{item['max_y']:5.1f}")
