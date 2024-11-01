from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from services.models import User  # Importation du modèle User
from services.db_service import get_sqlite_connection
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        logger.info("Tentative de connexion pour l'utilisateur: %s", username)

        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[2], password):
            login_user(User(id=user[0], username=user[1], password=user[2], role=user[3]))
            logger.info("Utilisateur %s connecté avec succès.", username)
            return redirect(url_for('auth_routes.dashboard'))
        else:
            logger.warning("Échec de la connexion pour l'utilisateur: %s", username)
            flash('Nom d utilisateur ou mot de passe incorrect', 'danger')

    return render_template('login.html')

@auth_routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'user')", (username, hashed_password))
        conn.commit()
        conn.close()

        logger.info("Nouvel utilisateur enregistré: %s", username)
        flash('Inscription reussie !', 'success')
        return redirect(url_for('auth_routes.login'))

    return render_template('signup.html')

@auth_routes.route('/logout')
@login_required
def logout():
    logger.info("Déconnexion de l'utilisateur: %s", current_user.username)
    logout_user()
    flash('Vous avez ete deconnecte', 'info')  # Ajoutez un message flash
    return redirect(url_for('main_routes.accueil'))  # Redirigez vers la page d'accueil

@auth_routes.route('/dashboard')
@login_required
def dashboard():
    logger.info("Accès au tableau de bord par l'utilisateur: %s", current_user.username)
    return render_template('dashboard.html')

@auth_routes.route('/gotosignup')
def gotosignup():
    return render_template('sign_up.html')
