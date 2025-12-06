import random
import json
import requests


import time

# URL de l'API locale pour récupérer les affaires
API_URL = "http://localhost:8001/affaires"

# Liste des prénoms et noms pour générer des individus fictifs
prenoms = ["Jean", "Paul", "Sophie", "Emma", "Lucas", "Léa", "Noah", "Alice", "Louis", "Chloé"]
noms = ["Dupont", "Martin", "Bernard", "Robert", "Richard", "Petit", "Durand", "Morel", "Fournier", "Girard"]

# Rôles possibles pour les individus
roles = ["témoin", "suspect", "victime"]

# Génération d'un numéro de téléphone fictif
def generate_phone_number():
    return f"+33{random.randint(600000000, 699999999)}"

# Récupération des affaires depuis l'API
try:
    response = requests.get(API_URL)
    response.raise_for_status()  # Vérifie si la requête est réussie
    affaires = response.json()
    affaires_ids = [affaire["_id"] for affaire in affaires] if affaires else []
except requests.exceptions.RequestException as e:
    print(f"Erreur lors de la récupération des affaires : {e}")
    affaires_ids = []

# Vérifie si au moins une affaire existe
if not affaires_ids:
    print("Aucune affaire récupérée. Vérifiez l'API et les données disponibles.")
    exit()

# Génération de 25 individus fictifs
# individus = []
# for _ in range(25):
#     individu = {
#         "nom": f"{random.choice(prenoms)} {random.choice(noms)}",
#         "date_naissance": f"{random.randint(1950, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
#         "role": random.choice(roles),
#         "telephone": generate_phone_number(),
#         "affaires": [random.choice(affaires_ids)]  # Associer un individu à une affaire existante
#     }
#     individus.append(individu)


individus = []

for _ in range(25):
    individu = {
        "nom": f"{random.choice(prenoms)} {random.choice(noms)}",
        "date_naissance": f"{random.randint(1950, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
        "role": random.choice(roles),
        "telephone": generate_phone_number(),
        "affaires": [affaires_ids[0]]  # Associer un individu à une affaire existante
    }

    individus.append(individu)


# Faire un filtrage sur les victimes



victimes = [individu for individu in individus if individu["role"] == "victime"] 

# Envoyer les victimes à l'api si ils existent
if victimes:
    victime_cible = victimes[0]
    response = requests.post("http://localhost:8001/individus", json=victime_cible)
    if response.status_code == 201:
        print(f"************* Individu de role {victime_cible['role']} appelé {victime_cible['nom']} enregistré avec succès *************")
    else:
        print("Erreur technique")
        print(response.content)


time.sleep(1)

suspects = [individu for individu in individus if individu["role"] == "suspect"]

# Envoyer les suspects à l'api si ils existent
if suspects:
    for suspect in suspects:
        response = requests.post("http://localhost:8001/individus", json=suspect)
        if response.status_code == 201:
            print(f"************* Individu de role {suspect['role']} appelé {suspect['nom']} enregistré avec succès *************")
            time.sleep(1)
        else:
            print("Erreur technique")
            print(response.content)
            break


temoins = [individu for individu in individus if individu["role"] == "témoin"]

# Envoyer les témoins à l'api si ils existent
if temoins:
    for temoin in temoins:
        response = requests.post("http://localhost:8001/individus", json=temoin)
        if response.status_code == 201:
            print(f"************* Individu de role {temoin['role']} appelé {temoin['nom']} enregistré avec succès *************")
            time.sleep(1)
        else:
            print("Erreur technique")
            print(response.content)
            break


# Sauvegarde des individus dans un fichier JSON
# with open("individus_fictifs.json", "w", encoding="utf-8") as f:
#     json.dump(individus, f, indent=4, ensure_ascii=False)

# # Affichage des 5 premiers individus générés
# print(json.dumps(individus[:5], indent=4, ensure_ascii=False))
