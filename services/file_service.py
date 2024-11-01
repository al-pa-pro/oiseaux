import sys
import os
import logging
from werkzeug.utils import secure_filename

# Configuration de base du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Chemin vers le dossier parent
dossier_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dossier_parent)

def allowed_file(filename, allowed_extensions):
    """Vérifie si le fichier a une extension autorisée."""
    is_allowed = '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    logging.debug("Vérification du fichier '%s' : %s", filename, is_allowed)
    return is_allowed

def save_file(file, upload_folder):
    """Sauvegarde le fichier dans le dossier spécifié si l'extension est autorisée."""
    if file and allowed_file(file.filename, Config.ALLOWED_EXTENSIONS):
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        
        try:
            file.save(file_path)
            logging.info("Fichier '%s' sauvegardé avec succès à '%s'", filename, file_path)
            return filename
        except Exception as e:
            logging.error("Erreur lors de la sauvegarde du fichier '%s': %s", filename, str(e))
            return None
    else:
        logging.warning("Le fichier '%s' n'est pas autorisé ou n'existe pas.", file.filename)
    return None

class Config:
    UPLOAD_FOLDER = 'static/uploads/'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'mp4', 'avi'}

    # Créer le dossier si nécessaire
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        logging.info("Dossier de téléchargement créé : '%s'", UPLOAD_FOLDER)
    else:
        logging.info("Dossier de téléchargement déjà existant : '%s'", UPLOAD_FOLDER)

    DATABASE = os.path.join(dossier_parent, 'BDDsqlite', 'oiseaux.db')  # Chemin vers la base de données

    logging.info("Base de données définie : '%s'", DATABASE)
