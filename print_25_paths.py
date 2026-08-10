import json

with open(r"d:\Escritorio\Data\paths_centroids.json", "r") as f:
    paths = json.load(f)

print(f"Total paths in original SVG: {len(paths)}")
for p in paths:
    print(f"Path {p['idx']:2d}: len={len(p['d']):4d} | cx={p['cx']:5.1f}, cy={p['cy']:5.1f} | X: {p['min_x']:5.1f}..{p['max_x']:5.1f} | Y: {p['min_y']:5.1f}..{p['max_y']:5.1f}")
