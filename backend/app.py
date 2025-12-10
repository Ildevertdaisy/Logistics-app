from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ariadne import make_executable_schema
from ariadne.asgi import GraphQL
from contextlib import asynccontextmanager
import logging
import os

from db_connection import ping_mongo_db_server, mongo_connection
from graph_db_connection import verify_connectivity, driver
from app_graphql.schema import type_defs
from app_graphql.resolvers import resolvers

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Démarrage
    logger.info(" Démarrage de l'API Galapagos")

    # Connexion MongoDB
    await ping_mongo_db_server()

    # Connexion Neo4J
    verify_connectivity()

    yield

    # Arrêt
    logger.info(" Arrêt de l'API Galapagos")
    mongo_connection.close()
    driver.close()


# Création de l'application FastAPI
app = FastAPI(
    title="API Galapagos - Richnou Galap",
    description="API GraphQL pour la gestion logistique de Richnou Galap aux îles Galapagos",
    version="1.0.0",
    lifespan=lifespan
)

def _get_allowed_origins():
    """Récupère les origines autorisées pour CORS depuis l'environnement."""
    raw_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )

    origins = [origin.strip().rstrip("/") for origin in raw_origins.split(",") if origin.strip()]
    logger.info("Origines CORS autorisées : %s", origins)
    return origins


# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Création du schéma GraphQL
schema = make_executable_schema(type_defs, resolvers)

# Montage de l'endpoint GraphQL
graphql_app = GraphQL(schema, debug=True)
app.mount("/graphql", graphql_app)


@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "Bienvenue sur l'API Richnou Galap - Galapagos",
        "version": "1.0.0",
        "endpoints": {
            "graphql": "/graphql",
            "graphql_playground": "/graphql (GET avec navigateur)"
        }
    }


@app.get("/health")
async def health_check():
    """Vérification de l'état de santé de l'API"""
    try:
        # Vérifier MongoDB
        mongo_ok = await ping_mongo_db_server()

        # Vérifier Neo4J
        neo4j_ok = verify_connectivity()

        return {
            "status": "healthy" if (mongo_ok and neo4j_ok) else "unhealthy",
            "mongodb": "connected" if mongo_ok else "disconnected",
            "neo4j": "connected" if neo4j_ok else "disconnected"
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
