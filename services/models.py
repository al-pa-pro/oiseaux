import sys
import os
import logging
from flask_login import UserMixin
from services.db_service import get_sqlite_connection

# Configuration de base du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Chemin vers le dossier parent
dossier_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dossier_parent)

# Modèle utilisateur
class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role

# Fonction pour charger un utilisateur depuis la base de données
def load_user(user_id):
    logging.info("Chargement de l'utilisateur avec l'ID : %s", user_id)
    conn = None
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user:
            logging.info("Utilisateur trouvé : %s", user)
            return User(id=user[0], username=user[1], password=user[2], role=user[3])
        else:
            logging.warning("Aucun utilisateur trouvé avec l'ID : %s", user_id)
            return None
            
    except Exception as e:
        logging.error("Erreur lors du chargement de l'utilisateur : %s", str(e))
        return None
    
    finally:
        if conn:
            conn.close()
            logging.info("Connexion à la base de données fermée.")

# Exemple d'utilisation de la fonction pour tester (optionnel)
if __name__ == "__main__":
    # Remplacez '1' par l'ID d'utilisateur que vous souhaitez charger pour tester
    load_user(1)
