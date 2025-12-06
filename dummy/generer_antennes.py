import pandas as pd
import random
import requests
import json
import time


# Liste des opérateurs télécoms fictifs
operateurs = ["Orange", "SFR", "Bouygues Telecom", "Free Mobile"]

# Liste de quelques villes françaises avec des coordonnées approximatives
villes_france = [
    {"nom": "Paris", "latitude": 48.8566, "longitude": 2.3522},
    {"nom": "Lyon", "latitude": 45.7640, "longitude": 4.8357},
    {"nom": "Marseille", "latitude": 43.2965, "longitude": 5.3698},
    {"nom": "Toulouse", "latitude": 43.6047, "longitude": 1.4442},
    {"nom": "Bordeaux", "latitude": 44.8378, "longitude": -0.5792},
    {"nom": "Lille", "latitude": 50.6292, "longitude": 3.0573},
    {"nom": "Nice", "latitude": 43.7102, "longitude": 7.2620},
    {"nom": "Nantes", "latitude": 47.2184, "longitude": -1.5536},
    {"nom": "Strasbourg", "latitude": 48.5734, "longitude": 7.7521},
    {"nom": "Montpellier", "latitude": 43.6108, "longitude": 3.8767},
    {"nom": "Rennes", "latitude": 48.1173, "longitude": -1.6778},
    {"nom": "Grenoble", "latitude": 45.1885, "longitude": 5.7245},
    {"nom": "Dijon", "latitude": 47.3220, "longitude": 5.0415},
    {"nom": "Le Havre", "latitude": 49.4944, "longitude": 0.1079},
    {"nom": "Reims", "latitude": 49.2583, "longitude": 4.0317}
]

# Liste des codes postaux fictifs
zones_couverture = [f"{random.randint(10000, 99999)}" for _ in range(100)]

# Fonction pour générer des coordonnées légèrement modifiées autour de la ville
def generate_coordinates(ville):
    return {
        "latitude": round(ville["latitude"] + random.uniform(-0.05, 0.05), 6),
        "longitude": round(ville["longitude"] + random.uniform(-0.05, 0.05), 6)
    }

# Génération de 25 antennes avec des localisations variées en France
antennes_france = []
for i in range(1, 26):
    ville = random.choice(villes_france)
    antenne = {
        "nom": f"Antenne {ville['nom']} {i}",
        "operateur": random.choice(operateurs),
        "coordonnees": generate_coordinates(ville),
        "zone_couverture": ", ".join(random.sample(zones_couverture, random.randint(2, 5)))
    }
    antennes_france.append(antenne)


    response = requests.post("http://localhost:8001/antennes", json=antenne)

    if response.status_code == 201:
        print(f"******************  Antenne {antenne['nom']} enregistré avec succès ******************")
    else:
        print("Erreur technique")
        print(response.content)
        break 
    time.sleep(1)

# Affichage des données sous forme de tableau
df_antennes_france = pd.DataFrame(antennes_france)
print(df_antennes_france)  # Remplace par un affichage adapté à ton usage
