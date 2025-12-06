from fastapi import FastAPI, Body, Depends
from fastapi.exceptions import HTTPException
from contextlib import asynccontextmanager
from db_connection import (ping_mongo_db_server,)

from graph_db_connection import driver, ajouter_individu, ajouter_noeud_antenne, ajouter_noeud_appel, ajouter_relation_telephonique

from bson import ObjectId
from models.models import *
from database import mongo_database
from fastapi.encoders import ENCODERS_BY_TYPE


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ping_mongo_db_server()
    yield


app = FastAPI(lifespan=lifespan)


ENCODERS_BY_TYPE[ObjectId] = str


@app.get("/")
async def root():
    return {"message": "Welcome to to the API !"}


# Fonctionnalités de l'api -> Endpoints sur les affaires 

@app.post("/affaires", status_code=201)
async def ajouter_affaire(
    data: AFFAIRE = Body(
        example={
            "titre": "Vole à main armée", 
            "description": "Vole à main armée", 
            "date": "2025-02-10T14:30:00", 
            "lieux": ["Paris"], 
            "suspects": [], 
            "temoins": [], 
            "telephonie": []
        }
    ), 
    mongo_db=Depends(mongo_database)):

    affaire = data.dict()

    await mongo_db.subjects.insert_one(affaire)

    return {
        "message": "Affaire enregistré avec succès",
        "id": affaire["_id"]
    }


@app.get("/affaires", status_code=200)
async def obtenir_tous_affaires(db=Depends(mongo_database)):

    affaires = []

    async for affaire in db.subjects.find({}):
        affaires.append(affaire)

    if not affaires:

        raise HTTPException(
            status_code=404,
            detail="Aucun affaire trouvé"
        )

    return affaires


@app.get("/affaires/{affaire_id}", status_code=200)
async def obtenir_affaire(affaire_id: str, db=Depends(mongo_database)):

    # Récupérer l'affaire souhaité
    affaire = await db.subjects.find_one(
        {
            "_id": ObjectId(affaire_id)
            if ObjectId.is_valid(affaire_id)
            else None
        }
    )

    print(affaire)

    if not affaire:
        raise HTTPException(
            status_code=404,
            detail="Affaire non trouvée."
        )
    
    return affaire


@app.put('/affaires/{affaire_id}')
async def modifier_affaire(
    affaire_id: str,
    affaire_donnees: dict,
    db = Depends(mongo_database)
    ):
    

    resultat = await db.subjects.update_one(
        {
            "_id": ObjectId(affaire_id)
            if ObjectId.is_valid(affaire_id)
            else None
        },
        {"$set": affaire_donnees}
    )

    if resutat.modified == 1:
        return {
            "message": "Affaire mise à jour avec succès !"
        }

    raise HTTPException(
        status_code=404, 
        detail="Affaire non trouvée."
    )

# Endpoint sur les lieux
@app.get("/lieux", status_code=200)
async def obtenir_lieux(mongo_db=Depends(mongo_database)):

    return {"message": "Test"}



# Endpoint sur les individus 
@app.post("/individus", status_code=201)
async def ajouter_individus(
    data: Individu = Body(
        example={
            "nom": "Jean Paul", 
            "date_naissance": "1984-02-10", 
            "role": "témoin", 
            "telephone": "+3306XXXXX", 
            "affaires": ["67a9f289f9b80820395fe96e"]
        }
    ), 
    mongo_db=Depends(mongo_database)):

    individu = data.dict()

    await mongo_db.individus.insert_one(individu)

    individu["individu_id"] = individu["_id"]

    # Créer le noeud neo4j correspondant
    with driver.session() as session:     
        session.execute_write(ajouter_individu, individu)

    return {
        "message": "Individu enregistré avec succès",
        "id": individu["_id"]
    }


@app.get("/individus/{individu_id}", status_code=200)
async def obtenir_individu(individu_id: str, db = Depends(mongo_database)):
    # Récupérer l'individu souhaité
    individu = await db.individus.find_one(
        {
            "_id": ObjectId(individu_id)
            if ObjectId.is_valid(individu_id)
            else None
        }
    )

    # print(individu)

    if not individu:
        raise HTTPException(
            status_code=404,
            detail="Individu non trouvée."
        )

    return individu


@app.get("/individus", status_code=200)
async def obtenir_tous_individus(db=Depends(mongo_database)):

    individus = []

    async for individu in db.individus.find({}):
        individus.append(individu)

    if not individus:

        raise HTTPException(
            status_code=404,
            detail="Aucun individu trouvé"
        )

    return individus


# Endpoint sur les temoignages
@app.post("/temoignages", status_code=201)
async def ajouter_temoignages(
    data: Temoignage = Body(
        example={
            "temoin": "67aa0b2617b9f010c6433e15", 
            "affaire": "67a9f289f9b80820395fe96e", 
            "description": "J'ai vu un homme en noir près de la voiture vers 23h.", 
        }
    ), 
    mongo_db=Depends(mongo_database)):

    temoignage = data.dict()

    await mongo_db.temoignages.insert_one(temoignage)

    return {
        "message": "Témoignage enregistré avec succès",
        "id": individu["_id"]
    }


@app.get("/temoignages/{temoignage_id}", status_code=200)
async def obtenir_temoignage(temoignage_id: str,
mongo_db = Depends(mongo_database)):

    # Récupérer le temoignage souhaité
    temoignage = await mongo_db.temoignages.find_one(
        {
            "_id": ObjectId(temoignage_id)
            if ObjectId.is_valid(temoignage_id)
            else None
        }
    )

    # print(temoignage)

    if not temoignage:
        raise HTTPException(
            status_code=404,
            detail="Temoignage non trouvée."
        )

    return individu


@app.get("/temoignages/recherche")
async def rechercher_temoignages(affaire: str, mongo_db=Depends(mongo_database)):
    recherche = await mongo_db.temoignages.find({"affaire": affaire})
    
    temoignages = await recherche.to_list(None)
    if temoignages:
       return temoignages
    else:
        raise HTTPException(
            status_code=404,
            detail="Temoignages non trouvés pour cette affaire"
        )


# Endpoints sur la téléphonie
@app.get("/antennes", status_code=200)
async def obtenir_antennes(mongo_db=Depends(mongo_database)):
    
    antennes = []

    async for antenne in mongo_db.antennes.find({}):
        antennes.append(antenne)

    if antennes:
        return antennes
    else:
        raise HTTPException(
            status_code=404,
            detail="Aucun antennes trouvés"
        )


@app.post("/antennes", status_code=201)
async def ajouter_antenne(
    data: Antenne = Body(
      example={
            "nom": "Antenne Paris Centre",
            "operateur": "Orange",
            "coordonnees": {
                "latitude": 48.8566,
                "longitude": 2.3522
            },
            "zone_couverture": "75001, 75002, 75003"
        }
    ),
    mongo_db = Depends(mongo_database)
    ):
    
    antenne = data.dict()
    await mongo_db.antennes.insert_one(antenne)


    # Créer le noeud neo4j correspondant
    with driver.session() as session:
        session.execute_write(ajouter_noeud_antenne, antenne)
        print("************* Antenne enregistré dans Neo4j *************")

    return {
        "message": "Antenne enregistré avec succès",
        "id": antenne["_id"]
    }


@app.post("/telephonie", status_code=201)
async def enregistrer_telephonie(data: Telephonie = Body(
    example={
        "appelant": "67aa0d90990f019fbbc2a337",
        "receveur": "67aa0d68990f019fbbc2a336",
        "date_heure": "2025-01-15T14:30:00",
        "duree": 120,
        "antenne": "Antenne Paris Centre"
    }),
    mongo_db=Depends(mongo_database)
    ):

    telephonie = data.dict()

    # Stocker les données d'un appel dans la base des données
    appel = {
        "date_heure": telephonie["date_heure"],
        "duree": telephonie["duree"]
    }

    await mongo_db.appels.insert_one(appel)

    print(f"************* Appel {appel['_id']} enregistré dans MongoDB *************")
    appel_id = f"Appel-{str(appel['_id'])}"

    # Créer le noeud appel neo4j correspondant
    with driver.session() as session:
        appel = {
            "appel_id": appel_id,
            "date_heure": telephonie["date_heure"],
            "duree": telephonie["duree"]
        }

        session.execute_write(ajouter_noeud_appel, appel)

        print("************* Appel enregistré dans Neo4j *************")


    # Créer les différentes relations possible
    with driver.session() as session:

        # Récupérer les données de l'appelant et receveur depuis mongo db
        donnees = {
        "appelant": telephonie["appelant"],
        "receveur": telephonie["receveur"],
        "antenne": telephonie["antenne"],
        "date_heure": telephonie["date_heure"],
        "appel": {
                "id": appel_id,
            }
        }

        session.execute_write(ajouter_relation_telephonique, donnees)

        print("************** Relations correspondantes créer avec succès dans Neo4j *********************")
        
    return {"message": "Communication téléphonique enregistrée avec succès !"}