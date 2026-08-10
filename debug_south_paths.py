import json

# Official 25 Department IDs (INEI standard):
# 1: Amazonas, 2: Ancash, 3: Apurimac, 4: Arequipa, 5: Ayacucho, 6: Cajamarca, 7: Callao, 8: Cusco, 9: Huancavelica, 10: Huanuco, 11: Ica, 12: Junin, 13: La Libertad, 14: Lambayeque, 15: Lima, 16: Loreto, 17: Madre de Dios, 18: Moquegua, 19: Pasco, 20: Piura, 21: Puno, 22: San Martin, 23: Tacna, 24: Tumbes, 25: Ucayali

# Let's map each SVG Path 0..24 to the 25 Peru Departments based on exact geographical coordinates:
# Path 0:  cx=435.2, cy=272.4 -> Ucayali (25)
# Path 1:  cx=494.3, cy=329.3 -> Madre de Dios (17)
# Path 2:  cx=362.5, cy=215.0 -> San Martin (22)
# Path 3:  cx=332.5, cy=170.8 -> Amazonas (1)
# Path 4:  cx=429.8, cy=149.6 -> Loreto (16)
# Path 5:  cx=422.1, cy=377.0 -> Ayacucho (5)
# Path 6:  cx=358.2, cy=331.0 -> Callao (7)
# Path 7:  cx=402.0, cy=354.8 -> Huancavelica (9)
# Path 8:  cx=402.4, cy=321.9 -> Junin (12)
# Path 9:  cx=362.0, cy=321.6 -> Lima (15)
# Path 10: cx=294.6, cy=199.8 -> Lambayeque (14)
# Path 11: cx=273.5, cy=141.6 -> Tumbes (24)
# Path 12: cx=444.7, cy=380.2 -> Cusco (8)
# Path 13: cx=454.2, cy=418.0 -> Arequipa (4)   <-- Note: Arequipa is huge south coast (Y: 393..455)
# Path 14: cx=515.9, cy=409.7 -> Puno (21)
# Path 15: cx=492.8, cy=445.8 -> Moquegua (18)  <-- Moquegua is between Arequipa and Tacna (Y: 424..466)
# Path 16: cx=503.8, cy=460.8 -> Tacna (23)    <-- Tacna is extreme south (Y: 444..480)
# Path 17: cx=338.8, cy=272.3 -> Ancash (2)
# Path 18: cx=314.1, cy=201.0 -> Cajamarca (6)
# Path 19: cx=377.4, cy=268.9 -> Huanuco (10)
# Path 20: cx=353.4, cy=332.0 -> Apurimac or Callao enclave? Wait!
# Path 21: cx=326.4, cy=235.3 -> La Libertad (13)
# Path 22: cx=389.8, cy=294.9 -> Pasco (19)
# Path 23: cx=279.6, cy=172.4 -> Piura (20)
# Path 24: cx=388.0, cy=380.7 -> Ica (11)

# Wait! Where is Apurimac? Apurimac is in Sierra, between Ayacucho (5), Cusco (8) and Arequipa (4)!
# Let's check Path 12 vs Path 13 vs Path 20!

with open(r"d:\Escritorio\Data\paths_centroids.json", "r") as f:
    paths = json.load(f)

for p in paths:
    print(f"Path {p['idx']:2d}: cx={p['cx']:5.1f}, cy={p['cy']:5.1f}, min_x={p['min_x']:5.1f}, max_x={p['max_x']:5.1f}, min_y={p['min_y']:5.1f}, max_y={p['max_y']:5.1f}")
