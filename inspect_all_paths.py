import json

with open(r"d:\Escritorio\Data\paths_centroids.json", "r") as f:
    paths = json.load(f)

for p in paths:
    idx = p['idx']
    cx, cy = p['cx'], p['cy']
    min_x, max_x = p['min_x'], p['max_x']
    min_y, max_y = p['min_y'], p['max_y']
    length = len(p['d'])
    print(f"Path {idx:2d}: len={length:4d} | cx={cx:5.1f}, cy={cy:5.1f} | X: {min_x:5.1f}..{max_x:5.1f} | Y: {min_y:5.1f}..{max_y:5.1f}")
