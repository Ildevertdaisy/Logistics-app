
from neo4j import GraphDatabase

uri = "bolt://graphdb:7687"
user="neo4j"
password="pleaseletmein"


driver = GraphDatabase.driver(uri, auth=(user, password))



# Fonctions utilitaires

def ajouter_individu(tx, individu: dict):

    # Préparer les données
    nom = individu["nom"]
    telephone = individu["telephone"]
    role = individu["role"]
    individu_id = str(individu["individu_id"])

    # Interagir avec Neo4j pour enregsitrer le noeud individu
    tx.run("CREATE (:Individu {nom: $nom, telephone: $telephone, role: $role, individu_id: $individu_id})", nom=nom, telephone=telephone, role=role, individu_id=individu_id)


def ajouter_noeud_antenne(tx, antenne: dict):
    # Préparer les données
    nom = antenne["nom"]
    operateur = antenne["operateur"]
    longitude = antenne["coordonnees"]["longitude"]
    latitude = antenne["coordonnees"]["latitude"]
    zone_couverture = antenne["zone_couverture"]

    # Interagir avec Neo4j pour enregistrer les données de l'antenne
    tx.run("CREATE (:Antenne {nom: $nom, operateur: $operateur, longitude: $longitude, latitude: $latitude, zone_couverture: $zone_couverture})", nom=nom, operateur=operateur, longitude=longitude, latitude=latitude,zone_couverture=zone_couverture)



def ajouter_noeud_appel(tx, appel: dict):
    # Préparer les données
    appel_id=appel["appel_id"]
    date_heure = appel["date_heure"]
    duree = appel["duree"]

    # Interagir avec Neo4j pour enregistrer les données de l'appel
    tx.run("CREATE (:Appel {date_heure: $date_heure, duree: $duree, appel_id: $appel_id})", date_heure=date_heure, duree=duree, appel_id=appel_id)


def ajouter_relation_telephonique(tx, donnees: dict):

    """
      Cette fonction permet d'ajouter une relation téléphonique 
      et celle-ci doit être de 4 types:
      A_APPELE, A_RECU_APPEL, A_ETE_EMIS_PAR, A_ETE_RECU_PAR, A_TRANSITE_PAR

      Ce type de reation téléphonique doit être définir dans le dictionnaire `donnees` (le deuxième paramètre) en tant que clé `relation_type`


      Exemple:
    """
    
    appelant = donnees["appelant"]
    receveur = donnees["receveur"]
    antenne = donnees["antenne"] 
    appel = donnees["appel"]["id"]
    date_heure = donnees["date_heure"]


    # Créer la relation a appelé
    query_1 = """
      MATCH (appelant:Individu) WHERE appelant.individu_id=$appelant MATCH (receveur:Individu) WHERE receveur.individu_id=$receveur CREATE (appelant)-[:A_APPELE {date_heure: $date_heure}]->(receveur) 
    """
    tx.run(query_1, appelant=appelant, receveur=receveur, date_heure=date_heure)


    # Créer la relation a reçu l'appel
    query_2 = """
      MATCH (appelant:Individu) WHERE appelant.individu_id=$appelant MATCH (receveur:Individu) WHERE receveur.individu_id=$receveur CREATE (appelant)-[:A_RECU_APPEL {date_heure: $date_heure}]->(receveur) 
    """
    tx.run(query_2, appelant=appelant, receveur=receveur, date_heure=date_heure)


    # Créer la relation a ete emis par
    query_3 = """
      MATCH (appel:Appel) WHERE appel.appel_id=$appel MATCH (appelant:Individu) WHERE appelant.individu_id=$appelant CREATE (appel)-[:A_ETE_EMIS_PAR {date_heure: $date_heure}]->(appelant) 
    """
    tx.run(query_3, appel=appel, appelant=appelant, date_heure=date_heure)

    # Créer la relation a été reçu par 
    query_4 = """
      MATCH (appel:Appel) WHERE appel.appel_id=$appel MATCH (receveur:Individu) WHERE receveur.individu_id=$receveur CREATE (appel)-[:A_ETE_RECU_PAR {date_heure: $date_heure}]->(receveur) 
    """
    tx.run(query_4, appel=appel, receveur=receveur, date_heure=date_heure)

    # Créer la relation a transité par
    query_5 = """
      MATCH (appel:Appel) WHERE appel.appel_id=$appel MATCH (antenne:Antenne) WHERE antenne.nom=$antenne CREATE (appel)-[:A_TRANSITE_PAR {date_heure: $date_heure}]->(antenne) 
    """
    tx.run(query_5, appel=appel, antenne=antenne, date_heure=date_heure)
