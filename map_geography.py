import json

with open(r"d:\Escritorio\Data\paths_centroids.json", "r") as f:
    paths = json.load(f)

# Official INEI department list and Backend IDs:
# 1: Amazonas, 2: Ancash, 3: Apurimac, 4: Arequipa, 5: Ayacucho, 6: Cajamarca, 7: Callao, 8: Cusco, 9: Huancavelica, 10: Huanuco, 11: Ica, 12: Junin, 13: La Libertad, 14: Lambayeque, 15: Lima, 16: Loreto, 17: Madre de Dios, 18: Moquegua, 19: Pasco, 20: Piura, 21: Puno, 22: San Martin, 23: Tacna, 24: Tumbes, 25: Ucayali

# Let's inspect all 25 paths carefully and match them:
for p in paths:
    idx = p['idx']
    cx, cy = p['cx'], p['cy']
    min_x, max_x = p['min_x'], p['max_x']
    min_y, max_y = p['min_y'], p['max_y']
    print(f"Path {idx:2d}: cx={cx:5.1f}, cy={cy:5.1f} | X: {min_x:5.1f}..{max_x:5.1f} | Y: {min_y:5.1f}..{max_y:5.1f}")
