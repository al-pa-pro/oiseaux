from flask import Blueprint, request, redirect, url_for, render_template, flash
from services.db_service import get_sqlite_connection
from services.file_service import save_file, Config
from routes.auth_routes import auth_routes, login_required
from flask_login import current_user
import logging

media_routes = Blueprint('media_routes', __name__)

# Configuration du logger
logger = logging.getLogger(__name__)

@media_routes.route('/ajouter_image/<int:oiseau_id>', methods=['POST'])
@login_required
def ajouter_image(oiseau_id):
    logger.info(f"Tentative d'ajouter une image pour l'oiseau avec l'ID {oiseau_id}.")
    
    if 'image' not in request.files:
        logger.warning('Aucune image trouvée dans la requête.')
        return redirect(url_for('oiseau_routes.afficher_oiseau', id=oiseau_id))

    image = request.files['image']
    image_filename = save_file(image, Config.UPLOAD_FOLDER) if image else None

    if image_filename:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO images (oiseau_id, filename)
            VALUES (?, ?)
        """, (oiseau_id, image_filename))
        conn.commit()
        conn.close()
        flash('Ajout proposé avec succès!', 'success')  # Message de confirmation
        logger.info(f"Image ajoutée avec succès : {image_filename} pour l'oiseau ID {oiseau_id}.")
    else:
        logger.error('Échec de l\'ajout de l\'image : le nom du fichier est vide.')
    
    return redirect(url_for('oiseau_routes.afficher_oiseau', id=oiseau_id))

@media_routes.route('/ajouter_audio/<int:oiseau_id>', methods=['POST'])
@login_required
def ajouter_audio(oiseau_id):
    logger.info(f"Tentative d'ajouter un audio pour l'oiseau avec l'ID {oiseau_id}.")
    
    if 'audio' not in request.files:
        logger.warning('Aucun audio trouvé dans la requête.')
        return redirect(url_for('oiseau_routes.afficher_oiseau', id=oiseau_id))

    audio = request.files['audio']
    audio_filename = save_file(audio, Config.UPLOAD_FOLDER) if audio else None

    if audio_filename:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audios (oiseau_id, filename)
            VALUES (?, ?)
        """, (oiseau_id, audio_filename))
        conn.commit()
        conn.close()
        flash('Ajout proposé avec succès!', 'success')  # Message de confirmation
        logger.info(f"Audio ajouté avec succès : {audio_filename} pour l'oiseau ID {oiseau_id}.")
    else:
        logger.error('Échec de l\'ajout de l\'audio : le nom du fichier est vide.')
    
    return redirect(url_for('oiseau_routes.afficher_oiseau', id=oiseau_id))

@media_routes.route('/ajouter_video/<int:oiseau_id>', methods=['POST'])
@login_required
def ajouter_video(oiseau_id):
    logger.info(f"Tentative d'ajouter une vidéo pour l'oiseau avec l'ID {oiseau_id}.")
    
    if 'video' not in request.files:
        logger.warning('Aucune vidéo trouvée dans la requête.')
        return redirect(url_for('oiseau_routes.afficher_oiseau', id=oiseau_id))

    video = request.files['video']
    video_filename = save_file(video, Config.UPLOAD_FOLDER) if video else None

    if video_filename:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO videos (oiseau_id, filename)
            VALUES (?, ?)
        """, (oiseau_id, video_filename))
        conn.commit()
        conn.close()
        flash('Ajout proposé avec succès!', 'success')  # Message de confirmation
        logger.info(f"Vidéo ajoutée avec succès : {video_filename} pour l'oiseau ID {oiseau_id}.")
    else:
        logger.error('Échec de l\'ajout de la vidéo : le nom du fichier est vide.')
    
    return redirect(url_for('oiseau_routes.afficher_oiseau', id=oiseau_id))

# Route pour afficher le formulaire de modification de la description
@media_routes.route('/modifier_description/<int:id>', methods=['GET', 'POST'])
@login_required
def modifier_description(id):
    if current_user.role != 'admin':
        flash("Seul un administrateur peut modifier la description des oiseaux.", "error")
        logger.warning(f"Accès refusé pour l'utilisateur {current_user.username} lors de la tentative de modification de la description de l'oiseau ID {id}.")
        return redirect(url_for('oiseau_routes.liste_oiseaux'))

    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT description FROM oiseaux WHERE id = ?", (id,))
    description = cursor.fetchone()
    cursor.execute("SELECT nom FROM oiseaux WHERE id = ?", (id,))
    nom_oiseau = cursor.fetchone()
    conn.close()

    if description is None:
        logger.error(f"Oiseau non trouvé avec l'ID {id}.")
        return "Oiseau non trouvé", 404

    if request.method == 'POST':
        nouvelle_description = request.form['description']
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE oiseaux
            SET description = ?
            WHERE id = ?
        """, (nouvelle_description, id))
        conn.commit()
        conn.close()
        flash('Modification proposée avec succès!', 'success')  # Message de confirmation
        logger.info(f"Description modifiée avec succès pour l'oiseau ID {id}.")
        return redirect(url_for('oiseau_routes.afficher_oiseau', id=id))

    return render_template('modifier_description.html', description=description[0], nom_oiseau=nom_oiseau[0], id=id)
