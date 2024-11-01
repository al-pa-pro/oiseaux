from sqlalchemy import create_engine
import pandas as pd
from flask import Blueprint, render_template
import logging
from dotenv import load_dotenv
import os


# Importer les variables d'environnement
load_dotenv()  # Charge les variables d'environnement depuis le fichier .env
POSTGRESQL_CONN = os.getenv("POSTGRESQL_CONN")


# Configuration de base du logging
logger = logging.getLogger(__name__)

pipeline_routes = Blueprint('pipeline_routes', __name__)

# Connexion à la base de données PostgreSQL
try:
    engine = create_engine(POSTGRESQL_CONN)
    logging.info("Connexion à la base de données PostgreSQL réussie.")
except Exception as e:
    logging.error("Erreur lors de la connexion à la base de données : %s", str(e))

@pipeline_routes.route('/tableau')
def tableau():
    """Route pour afficher un tableau des observations des oiseaux."""
    # Requête SQL pour récupérer les oiseaux présents au Nigeria
    query = """
    SELECT * FROM observations
    """
    
    try:
        # Récupérer les données dans un DataFrame
        df = pd.read_sql(query, engine)
        logging.info("Données récupérées avec succès : %d enregistrements.", len(df))
        
        # Passer les données au template
        return render_template('tableau.html', oiseaux=df.to_dict(orient='records'))
    except Exception as e:
        logging.error("Erreur lors de l'exécution de la requête : %s", str(e))
        return render_template('error.html', error=str(e))  # Renvoyer une page d'erreur


