import sys
import os
import logging
import sqlite3
from flask import current_app
from sqlalchemy import create_engine, exc, text, inspect

# Configuration de base du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Chemin vers le dossier parent
dossier_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dossier_parent)

def get_sqlite_connection():
    """Établit une connexion à la base de données SQLite."""
    try:
        conn = sqlite3.connect(current_app.config['DATABASE'])
        conn.row_factory = sqlite3.Row  # Accès par nom de colonne
        logging.info("Connexion à la base de données établie : '%s'", current_app.config['DATABASE'])
        return conn
    except sqlite3.Error as e:
        logging.error("Erreur lors de la connexion à la base de données : %s", str(e))
        return None
