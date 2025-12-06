import random
import json
from datetime import datetime, timedelta

import time

import requests

# Liste de titres et descriptions possibles d'affaires criminelles
titres_affaires = [
    "Vol à main armée", "Cambriolage", "Fraude bancaire", "Trafic de drogue",
    "Homicide volontaire", "Enlèvement", "Escroquerie", "Agression",
    "Incendie criminel", "Détournement de fonds", "Braquage de bijouterie",
    "Blanchiment d'argent", "Piraterie informatique", "Vol de voiture",
    "Falsification de documents"
]

# Liste des villes françaises possibles
villes_france = [
    "Paris", "Lyon", "Marseille", "Toulouse", "Bordeaux", "Lille",
    "Nice", "Nantes", "Strasbourg", "Montpellier", "Rennes",
    "Grenoble", "Dijon", "Le Havre", "Reims"
]

# Génération de 45 affaires criminelles avec des données variées
affaires = []
start_date = datetime(2024, 1, 1)  # Date de départ pour les dates aléatoires

for i in range(1, 46):
    ville = random.choice(villes_france)  # Choisir une ville au hasard
    titre = random.choice(titres_affaires)  # Choisir un titre d'affaire au hasard
    affaire = {
        "titre": titre,
        "description": titre,  # Même description que le titre
        "date": (start_date + timedelta(days=random.randint(1, 365))).isoformat(),
        "lieux": [ville],  # Assigner une ville
        "suspects": [],
        "temoins": [],
        "telephonie": []
    }
    affaires.append(affaire)

    response = requests.post("http://localhost:8001/affaires", json=affaire)


    if response.status_code == 201:
        print(f"******************  Antenne {affaire['titre']} enregistré avec succès ******************")
    else:
        print("Erreur technique")
        print(response.content)
        break

    time.sleep(1)

# Sauvegarde des affaires dans un fichier JSON
with open("affaires_fictives.json", "w", encoding="utf-8") as f:
    json.dump(affaires, f, indent=4, ensure_ascii=False)

# Affichage des 5 premières affaires générées
print(json.dumps(affaires[:5], indent=4, ensure_ascii=False))
