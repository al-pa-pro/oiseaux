from flask import Blueprint, render_template, request
from routes.auth_routes import auth_routes, login_required
import logging

main_routes = Blueprint('main_routes', __name__)

# Configuration du logger
logger = logging.getLogger(__name__)

@main_routes.route('/')
def accueil():
    logger.info("Accès à la page d'accueil.")
    return render_template('index.html')

@main_routes.route('/formulaire')
@login_required
def formulaire():
    nom = request.args.get('nom', '')  # Récupérer le paramètre, vide par défaut
    nom_scientifique = request.args.get('nom_scientifique', '')  # Récupérer le paramètre, vide par défaut
    code_oiseau = request.args.get('code_oiseau', '')
    
    logger.info(f"Accès à la page du formulaire. Paramètres reçus : nom='{nom}', nom_scientifique='{nom_scientifique}', code_oiseau='{code_oiseau}'")

    return render_template('formulaire.html', nom=nom, nom_scientifique=nom_scientifique, code_oiseau=code_oiseau)  # Passer le paramètre au template
