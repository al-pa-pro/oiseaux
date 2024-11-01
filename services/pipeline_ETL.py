import sys
import os

# Chemin vers le dossier parent
dossier_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(os.path.join(dossier_parent))


import requests
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, exc, text, inspect
import logging
from dotenv import load_dotenv

# Importer les variables d'environnement
load_dotenv()  # Charge les variables d'environnement depuis le fichier .env
POSTGRESQL_CONN = os.getenv("POSTGRESQL_CONN")
EBIRD_API_KEY = os.getenv("EBIRD_API_KEY")



# Configuration du logging
logging.basicConfig(
    #filename='mon_script.log',  # Nom du fichier de log
    level=logging.INFO,  # Niveau de log
    format='%(asctime)s - %(levelname)s - %(message)s'  # Format des messages
)
logger = logging.getLogger()

# Configuration de l'API eBird  
BASE_URL = 'https://api.ebird.org/v2/data/obs/geo/recent'

# Liste de villes avec leurs coordonnées et distance
locations = [
    {'lat': 6.5244, 'lng': 3.3792, 'dist': 50, 'name': 'Lagos, Nigeria'},
    {'lat': 9.0579, 'lng': 7.49508, 'dist': 50, 'name': 'Abuja, Nigeria'},
]

# Connexion à la base de données PostgreSQL
engine = create_engine(POSTGRESQL_CONN, client_encoding='utf8')

# Initialisation d'une liste pour stocker les résultats
all_data = []

# Requête pour chaque lieup
for loc in locations:
    params = {
        'lat': loc['lat'],
        'lng': loc['lng'],
        'dist': loc['dist']
    }
    
    headers = {'X-eBirdApiToken': EBIRD_API_KEY}
    try:
        response = requests.get(BASE_URL, params=params, headers=headers)

        # Vérification de la réponse
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)  # Convertir la réponse en DataFrame
            df['location'] = loc['name']  # Ajouter une colonne pour identifier la localisation
            all_data.append(df)  # Ajouter les résultats à la liste
            logger.info(f"Données récupérées pour {loc['name']}")
        else:
            logger.error(f"Erreur lors de la requête pour {loc['name']}: {response.status_code}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la connexion à l'API pour {loc['name']}: {e}")

# Concaténer tous les DataFrame en un seul
try:
    final_df = pd.concat(all_data, ignore_index=True)
    logger.info("Données concaténées avec succès.")
except Exception as e:
    logger.error(f"Erreur lors de la concaténation des DataFrames: {e}")

# Nettoyage des données
try:
    final_df = final_df.drop_duplicates(subset=['speciesCode', 'obsDt', 'location'])
    final_df['howMany'] = final_df['howMany'].fillna(1)
    logger.info("Nettoyage des données terminé.")

except Exception as e:
    logger.error(f"Erreur lors du nettoyage des données: {e}")

# Nettoyage des caractères non UTF-8
def clean_utf8(text):
    try:
        return text.encode('utf-8').decode('utf-8')
    except UnicodeDecodeError:
        return ''.join([c for c in text if ord(c) < 128])

# Nettoyer les colonnes de texte pour les erreurs d'encodage
try:
    for col in final_df.select_dtypes(include=['object']).columns:
        final_df[col] = final_df[col].apply(clean_utf8)
    logger.info("Nettoyage des chaînes UTF-8 terminé.")
except Exception as e:
    logger.error(f"Erreur lors du nettoyage des chaînes UTF-8: {e}")



# Connexion à SQLite
logging.info("Connexion à la base de données SQLite...")
sqlite_conn = sqlite3.connect("BDDsqlite\oiseaux.db")

# Récupérer les speciesCode des oiseaux qui ont une fiche dans SQLite
logging.info("Récupération des speciesCode avec une fiche dans SQLite...")
sqlite_cursor = sqlite_conn.cursor()
sqlite_query = "SELECT code,id FROM oiseaux WHERE status='approuvé';"
sqlite_cursor.execute(sqlite_query)
results=sqlite_cursor.fetchall()

species_with_fiches = {row[0]: row[1] for row in results}
logging.info(f"{len(species_with_fiches)} espèces avec une fiche trouvées dans SQLite.")




# Ajout de la colonne 'fiche_id' dans le DataFrame final_df
logging.info("Ajout de la colonne 'fiche_id' dans le DataFrame final_df...")
final_df['fiche_id'] = final_df['speciesCode'].apply(lambda x: species_with_fiches.get(x, None))
final_df['fiche_id']=final_df['fiche_id'].fillna(0)

# Afficher un aperçu pour vérification
logger.info("Aperçu des données avec la colonne 'fiche_id':")
logger.info(final_df[['speciesCode', 'fiche_id']])

# Vérification des doublons dans PostgreSQL avant insertion
def check_duplicates(df):
    with engine.connect() as connection:
        for index, row in df.iterrows():
            query = text("""
                SELECT COUNT(*) 
                FROM observations 
                WHERE "speciesCode" = :speciesCode 
                  AND "obsDt" = :obsDt 
                  AND "location" = :location
                  
            """)
            result = connection.execute(query, {
                'speciesCode': row['speciesCode'],
                'obsDt': row['obsDt'],
                'location': row['location']
            })
            count = result.scalar()
            if count > 0:
                df.drop(index, inplace=True)  # Supprimer les doublons
                logger.info(f"Doublon trouvé et supprimé: {row['speciesCode']} à {row['obsDt']} à {row['location']}")

#creation de la table si non existance
inspector = inspect(engine)
table_exists = 'observations' in inspector.get_table_names()

if not table_exists:
    # Création de la table avec la première ligne de final_df
    final_df.iloc[[0]].to_sql('observations', con=engine, if_exists='replace', index=False)
    logger.info("Table 'observations' créée avec la première ligne de final_df.")
else:
    logger.info("La table 'observations' existe déjà. Aucun enregistrement inséré.")


# Vérification des doublons
check_duplicates(final_df)

# Insérer les données dans la base PostgreSQL
if not final_df.empty:
    final_df.to_sql('observations', con=engine, if_exists='append', index=False, method='multi')
    logging.info("Insertion des données dans la base PostgreSQL...")
else:
    logging.info("Aucune donnée à insérer dans la base PostgreSQL.")

# Fermeture des connexions
sqlite_conn.close()
logging.info("Connexion à SQLite fermée.")
engine.dispose()
logging.info("Connexion à PostgreSQL fermée.")