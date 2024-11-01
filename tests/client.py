

import pytest
import os
import sys


# Chemin vers le dossier parent
dossier_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(dossier_parent)




from flask import Flask
import logging
from unittest import mock
from sqlalchemy import create_engine, exc
import requests
import pandas as pd
from flask_login import LoginManager
from services.db_service import get_sqlite_connection
from services.file_service import save_file 
from werkzeug.datastructures import FileStorage
from routes.main_routes import main_routes
from routes.form_routes import form_routes
from routes.oiseau_routes import oiseau_routes
from routes.media_routes import media_routes
from routes.auth_routes import auth_routes,login_required
from routes.admin_routes import admin_routes
from routes.pipeline_routes import pipeline_routes
from services.models import load_user, User
from services.init_admin import ajouter_admin
from werkzeug.security import generate_password_hash, check_password_hash
import tempfile
import sqlite3
from dotenv import load_dotenv

# Importer les variables d'environnement
load_dotenv()  # Charge les variables d'environnement depuis le fichier .env
POSTGRESQL_CONN = os.getenv("POSTGRESQL_CONN")
SECRET_KEY = os.getenv("SECRET_KEY")
EBIRD_API_KEY = os.getenv("EBIRD_API_KEY") 
CORTEX_API_KEY = os.getenv("CORTEX_API_KEY")
LOGIN_ADMIN = os.getenv("LOGIN_ADMIN")
MDP_ADMIN = os.getenv("MDP_ADMIN")
pw=generate_password_hash('pl')

@pytest.fixture
def app():
    """Configuration de l'application de test."""
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app.config['TESTING'] = True
    app.config["DATABASE"] = "BDDsqlite\oiseaux_test.db"
    app.register_blueprint(main_routes)
    app.register_blueprint(form_routes)
    app.register_blueprint(oiseau_routes)
    app.register_blueprint(media_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(admin_routes)
    app.register_blueprint(pipeline_routes)
    app.secret_key = SECRET_KEY
    app.config["UPLOAD_FOLDER"] = tempfile.gettempdir()  # Utiliser un dossier temporaire pour les uploads

    # Configuration de Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth_routes.login"



    @login_manager.user_loader
    def user_loader(user_id):
        return load_user(user_id)  # On utilise la fonction importée depuis models.py

    # Initialise la base de données pour les tests
    with app.app_context():
        init_database()
        yield app
        clean_database()

  # Renvoie l'application
@pytest.fixture(autouse=True)
def caplog(caplog):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Ou DEBUG pour plus de détails

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_database():
    """Nettoie la base de données de test après les tests et réinitialise les identifiants."""
    conn = get_sqlite_connection()
    cursor = conn.cursor()

    # Supprime toutes les données des tables
    cursor.execute("DELETE FROM videos")
    cursor.execute("DELETE FROM audios")
    cursor.execute("DELETE FROM images")
    cursor.execute("DELETE FROM oiseaux")
    cursor.execute("DELETE FROM users")


    # Réinitialiser les identifiants d'auto-incrémentation
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='oiseaux'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='images'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='audios'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='videos'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='users'")

    conn.commit()
    conn.close()

def init_database():
    """Initialise la base de données pour les tests."""
    conn = get_sqlite_connection()
    cursor = conn.cursor()

    # Créez les tables pour les oiseaux et insérez quelques données de test
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS oiseaux (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                nom_scientifique TEXT NOT NULL,
                code TEXT NOT NULL,
                description TEXT NOT NULL,
                status  TEXT NOT NULL  CHECK (status IN ("en attente", "approuvé") )  DEFAULT [en attente]
            )
            ''')

        # Créez les tables pour les oiseaux et insérez quelques données de test


    cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        oiseau_id INTEGER,
        filename TEXT,
        status  TEXT NOT NULL  CHECK (status IN ("en attente", "approuvé") )  DEFAULT [en attente],
        FOREIGN KEY (oiseau_id) REFERENCES oiseaux (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        oiseau_id INTEGER,
        filename TEXT,
        status  TEXT NOT NULL  CHECK (status IN ("en attente", "approuvé") )  DEFAULT [en attente],
        FOREIGN KEY (oiseau_id) REFERENCES oiseaux (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        oiseau_id INTEGER,
        filename TEXT,
        status  TEXT NOT NULL  CHECK (status IN ("en attente", "approuvé") )  DEFAULT [en attente],
        FOREIGN KEY (oiseau_id) REFERENCES oiseaux (id)
    )             
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT CHECK( role IN ('user','visitor','admin') ) NOT NULL DEFAULT 'visitor');
    ''')

    # Insérez des données de test
    cursor.execute("INSERT INTO users (username,password,role) VALUES (?,?, 'user')",("pili",pw))
    cursor.execute("INSERT INTO oiseaux (nom,nom_scientifique,code,description,status) VALUES ('Rouge-gorge','inconnu','eurrob1','description du rouge-gorge','approuvé')")
    cursor.execute("INSERT INTO oiseaux (nom,nom_scientifique,code,description,status) VALUES ('Merle','inconnu','inconnu','description du merle','en attente')")
    

    conn.commit()
    conn.close()

@pytest.fixture
def client(app):
    """Fournit un client de test pour l'application."""
    return app.test_client()

@pytest.fixture
def authenticated_client(client):
    with client:
        client.post('/login', data={'username': 'pili', 'password': 'pl'})  # Authentifiez l'utilisateur
        yield client  # Fournissez le client authentifié pour le reste des tests

@pytest.fixture
def admin_client(client): 
    with client:
        ajouter_admin()
        client.post('/login', data={'username': LOGIN_ADMIN, 'password': MDP_ADMIN})  # Authentifiez l'utilisateur
        yield client  # Fournissez le client authentifié pour le reste des tests