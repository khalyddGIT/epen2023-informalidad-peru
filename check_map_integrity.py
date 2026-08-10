import json

with open(r"d:\Escritorio\Data\frontend\src\peru_map_paths.json", "r") as f:
    data = json.load(f)

print(f"Total entries: {len(data)}")

# Check for duplicates or empty paths
paths_seen = {}
for i, d in enumerate(data):
    p = d['path']
    if p in paths_seen:
        print(f"DUPLICATE PATH: Index {i} ({d['name']}, id={d['id']}) has same path as Index {paths_seen[p]} ({data[paths_seen[p]]['name']})")
    else:
        paths_seen[p] = i

for d in data:
    if len(d['path']) < 200:
        print(f"SUSPICIOUS SHORT PATH: id={d['id']}, name={d['name']}, path_len={len(d['path'])}")
