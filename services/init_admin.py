import sys
import os
import logging
from werkzeug.security import generate_password_hash
from services.db_service import get_sqlite_connection
from flask import current_app
from dotenv import load_dotenv

# Importer les variables d'environnement
load_dotenv()  # Charge les variables d'environnement depuis le fichier .env
LOGIN_ADMIN = os.getenv("LOGIN_ADMIN")
MDP_ADMIN = os.getenv("MDP_ADMIN")

# Configuration de base du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Chemin vers le dossier parent
dossier_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dossier_parent)

def ajouter_admin():
    """Ajoute un utilisateur administrateur si celui-ci n'existe pas déjà dans la base de données."""
    logging.info("Démarrage de la fonction ajouter_admin.")
    
    admin_password = generate_password_hash(MDP_ADMIN)
    logging.info("Mot de passe pour l'utilisateur admin généré.")
    
    conn = None
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        # Insère l'utilisateur admin uniquement s'il n'existe pas déjà
        cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
                       (LOGIN_ADMIN, admin_password, "admin"))
        logging.info("Requête d'insertion exécutée pour l'utilisateur admin.")
        
        conn.commit()
        logging.info("Changements enregistrés dans la base de données.")
    
    except Exception as e:
        logging.error("Une erreur s'est produite lors de l'ajout de l'utilisateur admin : %s", str(e))
    
    finally:
        if conn:
            conn.close()
            logging.info("Connexion à la base de données fermée.")

# Appel de la fonction pour tester (optionnel)
if __name__ == "__main__":
    ajouter_admin()
