import matplotlib.pyplot as plt

# Listes pour stocker les données
gens = []
alive_counts = []
dead_counts = []

# Tenter d'ouvrir le fichier avec UTF-8, sinon utiliser Latin-1
try:
    with open("logs_fredkin.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
except UnicodeDecodeError:
    with open("logs_fredkin.txt", "r", encoding="latin-1") as f:
        lines = f.readlines()
else:
    lines = lines

# Traitement des lignes pour extraire les données
for line in lines:
    if "LOG," in line:
        parts = line.split("] ")
        if len(parts) == 2:
            data = parts[1]  # On récupère la partie après le timestamp
            fields = data.split(",")
            
            if len(fields) >= 5:
                gen_str = fields[2].split(":")[1]
                alive_str = fields[3].split(":")[1]
                dead_str = fields[4].split(":")[1]

                try:
                    g = int(gen_str)
                    a = int(alive_str)
                    d = int(dead_str)

                    gens.append(g)
                    alive_counts.append(a)
                    dead_counts.append(d)
                except ValueError:
                    continue

# Tracer les données
plt.figure(figsize=(10, 6))
plt.plot(gens, alive_counts, label="Alive", marker="o")
plt.plot(gens, dead_counts, label="Dead", marker="o")

plt.xlabel("Génération")
plt.ylabel("Nombre de cellules")
plt.title("Évolution du nombre de cellules vivantes et mortes (Fredkin)")
plt.legend()
plt.grid(True)
plt.show()
