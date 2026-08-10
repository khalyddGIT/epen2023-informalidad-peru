import json, re

log_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\7d7045ae-dbee-4ee4-ae92-92ea9f05ac28\.system_generated\logs\transcript_full.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Find all path tags with d=...
matches = re.findall(r'<path\s+d="([^"]+)"[^>]*fill="([^"]+)"', text)
print(f"Total path matches: {len(matches)}")

# Filter out fill="#000"
real_paths = [m for m in matches if m[1] != '#000']
print(f"Real department paths: {len(real_paths)}")

# Take the last 25 real paths
last_25 = real_paths[-25:]

out_data = []
for i, (d, fill) in enumerate(last_25):
    out_data.append({"index": i + 1, "fill": fill, "path": d})
    print(f"Dept {i+1}: fill={fill}, path_snippet={d[:30]}...")

with open(r"d:\Escritorio\Data\extracted_svg_paths.json", "w", encoding="utf-8") as out:
    json.dump(out_data, out, indent=2)

print("Saved 25 SVG paths to extracted_svg_paths.json")
