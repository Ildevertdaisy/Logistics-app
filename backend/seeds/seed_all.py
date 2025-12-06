"""
Script pour exécuter tous les seeds (MongoDB + Neo4J)
"""
import asyncio
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seed_mongodb import seed_data as seed_mongodb
from seed_neo4j import seed_neo4j


async def seed_all():
    """Exécuter tous les seeds"""
    print("=" * 60)
    print("🌱 SEED COMPLET - RICHNOU GALAP GALAPAGOS")
    print("=" * 60)
    print()

    # Seed MongoDB
    print("📍 ÉTAPE 1/2: MongoDB")
    print("-" * 60)
    await seed_mongodb()
    print()

    # Seed Neo4J
    print("📍 ÉTAPE 2/2: Neo4J")
    print("-" * 60)
    seed_neo4j()
    print()

    print("=" * 60)
    print("✅ SEED COMPLET TERMINÉ AVEC SUCCÈS!")
    print("=" * 60)
    print()
    print("Vous pouvez maintenant:")
    print("  - Accéder à l'API GraphQL: http://localhost:8000/graphql")
    print("  - Consulter Neo4J Browser: http://localhost:7474")
    print("  - Se connecter à MongoDB sur: localhost:27017")
    print()


if __name__ == "__main__":
    asyncio.run(seed_all())
