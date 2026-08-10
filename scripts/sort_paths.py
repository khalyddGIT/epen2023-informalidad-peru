import json, re

with open(r"d:\Escritorio\Data\paths_centroids.json", "r") as f:
    paths = json.load(f)

# Let's list all 25 paths by their bounding boxes:
sorted_by_y = sorted(paths, key=lambda p: (p['cy'], p['cx']))

print("Sorted by CY, CX:")
for p in sorted_by_y:
    print(f"Path {p['idx']:2d}: cx={p['cx']:5.1f}, cy={p['cy']:5.1f} | X: {p['min_x']:5.1f}..{p['max_x']:5.1f} | Y: {p['min_y']:5.1f}..{p['max_y']:5.1f} | len={len(p['d'])}")
