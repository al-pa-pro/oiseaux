from flask import Blueprint, request, redirect, url_for, flash, jsonify
from services.db_service import get_sqlite_connection
from services.file_service import save_file, Config
from routes.auth_routes import auth_routes, login_required
from services.cortextext_service import generate_description
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

form_routes = Blueprint('form_routes', __name__)

@form_routes.route('/soumettre', methods=['POST'])
@login_required
def soumettre():
    logger.info("Début de la soumission d'un oiseau.")
    
    if request.method == 'POST':
        nom = request.form['nom']
        nom_scientifique = request.form['nom_scientifique']
        code = request.form['code']
        description = request.form['description']
        
        logger.info("Données reçues: nom: %s, nom_scientifique: %s, code: %s", nom, nom_scientifique, code)

        # Remplacer les sauts de ligne par des balises <br>
        formatted_description = description.replace('\n', '<br>')
        conn = get_sqlite_connection()
        cursor = conn.cursor()

        logger.info("Insertion dans la base de données.")
        cursor.execute("""
            INSERT INTO oiseaux (nom, nom_scientifique, code, description)
            VALUES (?, ?, ?, ?)
        """, (nom, nom_scientifique, code, formatted_description))

        oiseau_id = cursor.lastrowid
        logger.info("Oiseau inséré")

        # Gestion des fichiers
        audio = request.files.get('audio')
        video = request.files.get('video')
        images = request.files.getlist('images')

        logger.info("Fichiers reçus")

        # Sauvegarder les fichiers
        audio_filename = save_file(audio, Config.UPLOAD_FOLDER) if audio else None
        video_filename = save_file(video, Config.UPLOAD_FOLDER) if video else None
        image_filenames = [save_file(image, Config.UPLOAD_FOLDER) for image in images if image]

        # Insérer les fichiers dans la base de données
        if audio_filename:
            logger.info("Insertion de l'audio: %s", audio_filename)
            cursor.execute("""
                INSERT INTO audios (oiseau_id, filename)
                VALUES (?, ?)
            """, (oiseau_id, audio_filename))

        if video_filename:
            logger.info("Insertion de la vidéo: %s", video_filename)
            cursor.execute("""
                INSERT INTO videos (oiseau_id, filename)
                VALUES (?, ?)
            """, (oiseau_id, video_filename))

        for image_filename in image_filenames:
            logger.info("Insertion de l'image: %s", image_filename)
            cursor.execute("""
                INSERT INTO images (oiseau_id, filename)
                VALUES (?, ?)
            """, (oiseau_id, image_filename))

        conn.commit()
        conn.close()
        logger.info("Soumission réussie. Oiseau proposé avec succès!")
        flash('Oiseau proposé avec succès!', 'success')  # Message de confirmation
        return redirect(url_for('main_routes.accueil'))

@form_routes.route('/generate_description', methods=['POST'])
@login_required
def generate_description_route():
    """Route pour générer une description automatiquement depuis le prompt"""
    data = request.json
    nom_scientifique = data.get('nom_scientifique', '')
    custom_prompt = data.get('custom_prompt', f"Donne moi une description enthousiaste de l'oiseau {nom_scientifique} en utilisant son nom français:")

    logger.info("Génération de description pour: %s", nom_scientifique)

    try:
        # Génération de la description via le site cortextext et son API
        description = generate_description(custom_prompt)
        logger.info("Description générée avec succès.")
        return jsonify({'description': description})
    except Exception as e:
        logger.error("Erreur lors de la génération de la description: %s", str(e))
        return jsonify({'error': str(e)}), 500
