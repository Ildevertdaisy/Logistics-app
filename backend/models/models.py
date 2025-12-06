
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Dict, Optional

from enum import Enum


class AFFAIRE(BaseModel):

    titre: str
    description: str
    date: datetime
    lieux: List[str]
    suspects: Optional[List[str]] = []
    temoins: Optional[List[str]] = []
    telephonie: Optional[List[str]] = []


# class Coordonnees(BaseModel):
    
#     latitude: float
#     longitude: float


class Lieux(BaseModel):
    nom: str
    adresse: str
    coordonnees: Optional[dict[str, str]] = {}


# Les modèles reliés aux aux individus (les suspects, les témoins et les victimes)

class RoleIndividu(Enum):
    TEMOIN = "témoin"
    SUSPECT = "suspect"
    VICTIME = "victime"



class Individu(BaseModel):

    nom: str
    date_naissance: datetime
    role: str
    telephone: str
    affaires: List[str]


# Le modèle à propos des temoignages (les déclaration des témoins)

class Temoignage(BaseModel):

    temoin: str
    affaire: str
    description: str


# Modèles à propos de le téléphonie

class Appel(BaseModel):

    date: datetime
    duree: int

class Antenne(BaseModel):

    nom: str
    operateur: str
    coordonnees:  dict[str, float]
    zone_couverture: str


class Telephonie(BaseModel):
    appelant: str
    receveur: str
    date_heure: datetime
    duree: int
    antenne: str