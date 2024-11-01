from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from services.db_service import get_sqlite_connection
from routes.auth_routes import auth_routes, login_required
from flask_login import current_user
from sqlalchemy import create_engine, exc, text
import logging
from dotenv import load_dotenv
import os


# Importer les variables d'environnement
load_dotenv()  # Charge les variables d'environnement depuis le fichier .env
POSTGRESQL_RENDER_CONN = os.getenv("POSTGRESQL_RENDER_CONN")


# Configuration du logging
logger = logging.getLogger(__name__)

oiseau_routes = Blueprint('oiseau_routes', __name__)

@oiseau_routes.route('/liste_oiseaux')
def liste_oiseaux():
    logging.info("Accès à la liste des oiseaux.")

    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id,code,nom FROM oiseaux WHERE status= 'approuvé'")
    oiseaux = cursor.fetchall()
    conn.close()
    logging.info("Liste des oiseaux récupérée avec succès : %d enregistrements.", len(oiseaux))
    return render_template('liste_oiseaux.html', oiseaux=oiseaux)
    


@oiseau_routes.route('/oiseau/<int:id>')
def afficher_oiseau(id):
    logging.info("Affichage des détails de l'oiseau avec ID: %d", id)

    if not current_user.is_authenticated or (current_user.is_authenticated and current_user.role != 'admin'):
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM oiseaux WHERE id = ? and status= 'approuvé'", (id,))
        oiseau = cursor.fetchone()

        if oiseau is None:
            logging.warning("Oiseau avec ID: %d non trouvé.", id)
            return "Oiseau non trouve", 404

        cursor.execute("SELECT * FROM images WHERE oiseau_id = ? AND status= 'approuvé'", (id,))
        images = cursor.fetchall()

        cursor.execute("SELECT * FROM audios WHERE oiseau_id = ? AND status= 'approuvé'", (id,))
        audios = cursor.fetchall()

        cursor.execute("SELECT * FROM videos WHERE oiseau_id = ? AND status= 'approuvé'", (id,))
        videos = cursor.fetchall()

        conn.close()
        logging.info("Détails de l'oiseau avec ID: %d affichés.", id)
        return render_template('oiseau.html', oiseau=oiseau, images=images, audios=audios, videos=videos)

    if current_user.role == 'admin':
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM oiseaux WHERE id = ?", (id,))
        oiseau = cursor.fetchone()

        if oiseau is None:
            logging.warning("Oiseau avec ID: %d non trouvé.", id)
            return "Oiseau non trouvé", 404

        cursor.execute("SELECT * FROM images WHERE oiseau_id = ?", (id,))
        images = cursor.fetchall()

        cursor.execute("SELECT * FROM audios WHERE oiseau_id = ?", (id,))
        audios = cursor.fetchall()

        cursor.execute("SELECT * FROM videos WHERE oiseau_id = ?", (id,))
        videos = cursor.fetchall()

        conn.close()
        logging.info("Détails de l'oiseau avec ID: %d affichés.", id)
        return render_template('oiseau.html', oiseau=oiseau, images=images, audios=audios, videos=videos)

@oiseau_routes.route('/changer_edit_mode/')
@login_required
def changer_edit_mode():
    session['edit_mode'] = not session.get('edit_mode', False)
    logging.info("Mode d'édition changé à: %s", session['edit_mode'])
    return redirect(request.referrer)

@oiseau_routes.route('/oiseau/<int:id>/<string:type>/<int:typeid>/valider', methods=['POST'])
@login_required
def valider_proposition(id, type, typeid):
    if current_user.role != 'admin':
        flash('Accès réservé aux administrateurs.', 'danger')
        logging.warning("Accès refusé pour validation de la proposition ID: %d", id)
        return redirect(url_for('main_routes.accueil'))

    # Définir la table selon le type
    table = ""
    if type == "nom":
        table = "oiseaux"
    elif type == "description":
        table = "descriptions"
    elif type == "image":
        table = "images"
    elif type == "audio":
        table = "audios"
    elif type == "video":
        table = "videos"

    if table == "oiseaux":
        sqlite_conn = get_sqlite_connection()
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT code FROM oiseaux WHERE id=?", (id,))
        code = sqlite_cursor.fetchall()

        if code:  # Vérifier si un résultat a été trouvé
            # Connexion à PostgreSQL via SQLAlchemy
            postgresql_conn = create_engine(POSTGRESQL_RENDER_CONN, client_encoding='utf8')

            # Requête SQL pour mettre à jour "fiche_id"
            sql = text("""
                UPDATE observations
                SET "fiche_id" = :fiche_id
                WHERE "speciesCode" = :speciesCode
            """)
            # Avant d'exécuter la requête
            logging.info(f"fiche_id: {id}, speciesCode: {code[0]['code']}")

            # Exécution de la requête dans PostgreSQL en passant les paramètres de manière sécurisée
            with postgresql_conn.connect() as conn:
                conn.execute(sql, {"fiche_id": id, "speciesCode": code[0]['code']})  # code[0] pour récupérer le premier élément du résultat
                conn.commit()
                logging.info("fiche_id mis à jour avec succès pour speciesCode: %s", code[0]['code'])

    # Fermeture des connexions
    sqlite_conn.close()

    conn = get_sqlite_connection()
    cursor = conn.cursor()

    # Mettre à jour le statut
    cursor.execute(f"UPDATE {table} SET status = ? WHERE id = ?", ("approuvé", typeid))

    conn.commit()
    conn.close()

    flash(f"Proposition de {type} validée avec succès", "success")
    logging.info("Proposition de %s validée avec succès pour ID: %d", type, typeid)
    return redirect(url_for('oiseau_routes.afficher_oiseau', id=id))

@oiseau_routes.route('/oiseau/<int:id>/<string:type>/<int:typeid>/cacher', methods=['POST'])
@login_required
def cacher_proposition(id, type, typeid):
    if current_user.role != 'admin':
        flash('Accès réservé aux administrateurs.', 'danger')
        logging.warning("Accès refusé pour cacher la proposition ID: %d", id)
        return redirect(url_for('main_routes.accueil'))

    conn = get_sqlite_connection()
    cursor = conn.cursor()

    # Définir la table selon le type
    table = ""
    if type == "nom":
        table = "oiseaux"
    elif type == "description":
        table = "descriptions"
    elif type == "image":
        table = "images"
    elif type == "audio":
        table = "audios"
    elif type == "video":
        table = "videos"

    # Mettre à jour le statut
    cursor.execute(f"UPDATE {table} SET status = ? WHERE id = ?", ("en attente", typeid))

    conn.commit()
    conn.close()

    if table == "oiseaux":
        sqlite_conn = get_sqlite_connection()
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT code FROM oiseaux WHERE id=?", (id,))
        code = sqlite_cursor.fetchall()
        sqlite_conn.close()

        if code:  # Vérifier si un résultat a été trouvé
            # Connexion à PostgreSQL via SQLAlchemy
            postgresql_conn = create_engine(POSTGRESQL_RENDER_CONN, client_encoding='utf8')

            # Requête SQL pour mettre à jour "fiche_id"
            sql = text("""
                UPDATE observations
                SET "fiche_id" = 0
                WHERE "speciesCode" = :speciesCode
            """)

            # Exécution de la requête dans PostgreSQL en passant les paramètres de manière sécurisée
            with postgresql_conn.connect() as conn:
                conn.execute(sql, {"speciesCode": code[0]["code"]})  # code[0] pour récupérer le premier élément du résultat
                conn.commit()
                logging.info("fiche_id caché pour speciesCode: %s", code[0]["code"])

    flash(f"Proposition de {type} cachée avec succès", "success")
    logging.info("Proposition de %s cachée avec succès pour ID: %d", type, typeid)
    return redirect(url_for('oiseau_routes.afficher_oiseau', id=id))

@oiseau_routes.route('/oiseau/<int:id>/<string:type>/<int:typeid>/refuser', methods=['POST'])
@login_required
def supprimer_oiseau(id, type, typeid):
    if current_user.role != 'admin':
        flash('Accès réservé aux administrateurs.', 'danger')
        logging.warning("Accès refusé pour refuser la proposition ID: %d", id)
        return redirect(url_for('main_routes.accueil'))

    # Définir la table selon le type
    table = ""
    if type == "nom":
        table = "oiseaux"
    elif type == "description":
        table = "descriptions"
    elif type == "image":
        table = "images"
    elif type == "audio":
        table = "audios"
    elif type == "video":
        table = "videos"

    # Remise à 0 de l'id dans POSTGRESQL
    if table == "oiseaux":
        sqlite_conn = get_sqlite_connection()
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT code,status FROM oiseaux WHERE id=?", (id,))
        oiseau = sqlite_cursor.fetchall()
        code=oiseau[0][0]
        status=oiseau[0][1]

        sqlite_conn.close()

        if code and status=="approuvé":  # Vérifier si un résultat a été trouvé
            # Connexion à PostgreSQL via SQLAlchemy
            postgresql_conn = create_engine(POSTGRESQL_RENDER_CONN, client_encoding='utf8')

            # Requête SQL pour mettre à jour "fiche_id"
            sql = text("""
                UPDATE observations
                SET "fiche_id" = 0
                WHERE "speciesCode" = :speciesCode
            """)

            # Exécution de la requête dans PostgreSQL en passant les paramètres de manière sécurisée
            with postgresql_conn.connect() as conn:
                conn.execute(sql, {"speciesCode": code})  # code[0] pour récupérer le premier élément du résultat
                conn.commit()
                logging.info("fiche_id supprimé pour speciesCode: %s", code)
            

    # Supprimer la proposition rejetée
    conn = get_sqlite_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM oiseaux WHERE id = ?", (typeid,))
    cursor.execute("DELETE FROM images WHERE oiseau_id= ?", (typeid,))
    cursor.execute("DELETE FROM audios WHERE oiseau_id= ?", (typeid,))
    cursor.execute("DELETE FROM videos WHERE oiseau_id= ?", (typeid,))

    conn.commit()
    conn.close()


    flash(f"Proposition de {type} refusée avec succès", "success")
    logging.info("Proposition de %s refusée avec succès pour ID: %d", type, typeid)
    return redirect(url_for('main_routes.accueil'))
