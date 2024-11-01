from flask import Blueprint, render_template, redirect, url_for, flash, request
from services.db_service import get_sqlite_connection
from services.file_service import save_file
from routes.auth_routes import auth_routes, login_required
from flask_login import login_required, current_user

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/liste_propositions', methods=['GET'])
@login_required
def liste_propositions():
    if current_user.role != 'admin':
        flash('Accès réservé aux administrateurs.', 'danger')
        return redirect(url_for('main_routes.accueil'))

    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT oiseaux.id, oiseaux.code, oiseaux.nom, images.oiseau_id, images.status, videos.oiseau_id, videos.status, audios.oiseau_id, audios.status
    FROM oiseaux
    LEFT JOIN images ON images.oiseau_id = oiseaux.id 
    LEFT JOIN videos ON videos.oiseau_id = oiseaux.id
    LEFT JOIN audios ON audios.oiseau_id = oiseaux.id 
    WHERE oiseaux.status = 'en attente' OR images.status = 'en attente' OR videos.status = 'en attente' OR audios.status = 'en attente'
""")
    propositions = cursor.fetchall()
    conn.close()
    return render_template('liste_propositions.html', propositions=propositions)


