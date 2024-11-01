import sys
import os

# Chemin vers le dossier parent
dossier_parent = os.path.dirname(os.path.abspath(__file__))
print(dossier_parent)

sys.path.append(dossier_parent)

from flask import Flask
import logging
from services.file_service import Config
from services.models import load_user
from flask_login import LoginManager
from services.init_admin import ajouter_admin
from services.db_service import get_sqlite_connection
from dotenv import load_dotenv

# Importer les variables d'environnement
load_dotenv()  # Charge les variables d'environnement depuis le fichier .env
POSTGRESQL_RENDER_CONN = os.getenv("POSTGRESQL_RENDER_CONN")
SECRET_KEY = os.getenv("SECRET_KEY")


# Importer les modules de routes
from routes.main_routes import main_routes
from routes.form_routes import form_routes
from routes.oiseau_routes import oiseau_routes
from routes.media_routes import media_routes
from routes.auth_routes import auth_routes
from routes.admin_routes import admin_routes
from routes.pipeline_routes import pipeline_routes


app = Flask(__name__)
app.secret_key = SECRET_KEY

# Configuration du logging
def setup_logging():
    logging.basicConfig(level=logging.INFO,  # Changez à DEBUG pour plus de détails
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    return logger

logger = setup_logging()

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth_routes.login"

# Fonction pour charger un utilisateur
@login_manager.user_loader
def user_loader(user_id):
    logging.info(f"Chargement de l'utilisateur avec ID: {user_id}")
    return load_user(user_id)  # On utilise la fonction importée depuis models.py

# Charger la configuration
app.config.from_object(Config)

# Enregistrer les blueprints
app.register_blueprint(main_routes)
app.register_blueprint(form_routes)
app.register_blueprint(oiseau_routes)
app.register_blueprint(media_routes)
app.register_blueprint(auth_routes)
app.register_blueprint(admin_routes)
app.register_blueprint(pipeline_routes)

if __name__ == '__main__':
    with app.app_context():  # Crée un contexte d'application
        logging.info("Création initiale des tables si elles n'existent pas.")

        conn = get_sqlite_connection()
        cursor = conn.cursor()

        try:
            # Créez les tables pour les oiseaux et insérez quelques données de test
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS oiseaux (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL,
                    nom TEXT NOT NULL,
                    nom_scientifique TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status  TEXT NOT NULL  CHECK (status IN ("en attente", "approuvé") )  DEFAULT [en attente]
                )
            ''')
            logging.info("Table 'oiseaux' vérifiée ou créée avec succès.")

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    oiseau_id INTEGER,
                    filename TEXT,
                    status  TEXT NOT NULL  CHECK (status IN ("en attente", "approuvé") )  DEFAULT [en attente],
                    FOREIGN KEY (oiseau_id) REFERENCES oiseaux (id)
                )
            ''')
            logging.info("Table 'images' vérifiée ou créée avec succès.")

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    oiseau_id INTEGER,
                    filename TEXT,
                    status  TEXT NOT NULL  CHECK (status IN ("en attente", "approuvé") )  DEFAULT [en attente],
                    FOREIGN KEY (oiseau_id) REFERENCES oiseaux (id)
                )
            ''')
            logging.info("Table 'audios' vérifiée ou créée avec succès.")

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    oiseau_id INTEGER,
                    filename TEXT,
                    status  TEXT NOT NULL  CHECK (status IN ("en attente", "approuvé") )  DEFAULT [en attente],
                    FOREIGN KEY (oiseau_id) REFERENCES oiseaux (id)
                )
            ''')
            logging.info("Table 'videos' vérifiée ou créée avec succès.")

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT CHECK( role IN ('user','visitor','admin') ) NOT NULL DEFAULT 'visitor'
                );
            ''')
            logging.info("Table 'users' vérifiée ou créée avec succès.")

            conn.commit()
            logging.info("Toutes les modifications de la base de données ont été validées.")
        except Exception as e:
            logging.error(f"Erreur lors de la création des tables : {e}")
            conn.rollback()  # Annule les modifications en cas d'erreur
        finally:
            conn.close()  # Toujours fermer la connexion
            logging.info("Connexion à la base de données fermée.")

        ajouter_admin()  # Appelle la fonction pour ajouter l'administrateur
        logging.info("Vérification et ajout de l'administrateur effectué.")
    # Utiliser le port fourni par Render
    port = int(os.environ.get("PORT", 5000))  # 5000 est la valeur par défaut pour un environnement local
    app.run(host='0.0.0.0', port=port, debug=False)    

