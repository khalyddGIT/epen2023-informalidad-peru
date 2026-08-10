import json

with open(r"d:\Escritorio\Data\paths_centroids.json", "r") as f:
    paths = json.load(f)

for idx in [6, 12, 13, 15, 20]:
    p = paths[idx]
    print(f"--- PATH {idx} ---")
    print(f"cx={p['cx']}, cy={p['cy']}, bounds=({p['min_x']}..{p['max_x']}, {p['min_y']}..{p['max_y']})")
    print(f"d snippet: {p['d'][:100]}...")
