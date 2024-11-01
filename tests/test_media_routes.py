from tests.client import *



def test_ajouter_image(authenticated_client):
    """Test pour l'ajout d'une image."""
    image_path = os.path.join(authenticated_client.application.config["UPLOAD_FOLDER"], 'test_image.jpg')
    with open(image_path, 'wb') as f:
        f.write(os.urandom(1024))  # Création d'un fichier image fictif

    with open(image_path, 'rb') as img:
        response = authenticated_client.post('/ajouter_image/1', data={'image': img})

    assert response.status_code == 302  # Redirection
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM images WHERE oiseau_id = 1")
    image = cursor.fetchone()
    conn.close()
    assert image is not None
    
    assert image[2]  == "C_Users_alexa_AppData_Local_Temp_test_image.jpg"  # Assurez-vous que le nom du fichier est correct

def test_ajouter_audio(authenticated_client):
    """Test pour l'ajout d'un audio."""
    audio_path = os.path.join(authenticated_client.application.config["UPLOAD_FOLDER"], 'test_audio.mp3')
    with open(audio_path, 'wb') as f:
        f.write(os.urandom(1024))  # Création d'un fichier audio fictif

    with open(audio_path, 'rb') as audio:
        response = authenticated_client.post('/ajouter_audio/1', data={'audio': audio})

    assert response.status_code == 302  # Redirection
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audios WHERE oiseau_id = 1")
    audio_record = cursor.fetchone()
    conn.close()

    assert audio_record is not None
    assert audio_record[2] == 'C_Users_alexa_AppData_Local_Temp_test_audio.mp3'  # Assurez-vous que le nom du fichier est correct

def test_ajouter_video(authenticated_client):
    """Test pour l'ajout d'une vidéo."""
    video_path = os.path.join(authenticated_client.application.config["UPLOAD_FOLDER"], 'test_video.mp4')
    with open(video_path, 'wb') as f:
        f.write(os.urandom(1024))  # Création d'un fichier vidéo fictif

    with open(video_path, 'rb') as video:
        response = authenticated_client.post('/ajouter_video/1', data={'video': video})

    assert response.status_code == 302  # Redirection
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos WHERE oiseau_id = 1")
    video_record = cursor.fetchone()
    conn.close()

    assert video_record is not None
    assert video_record[2] == 'C_Users_alexa_AppData_Local_Temp_test_video.mp4'  # Assurez-vous que le nom du fichier est correct

def test_modifier_description(admin_client):
    """Test pour la modification de la description d'un oiseau."""
    response = admin_client.post('/modifier_description/1', data={'description': 'Nouvelle description'})
    assert response.status_code == 302  # Redirection

    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT description FROM oiseaux WHERE id = 1")
    description = cursor.fetchone()
    conn.close()

    assert description[0] == 'Nouvelle description'  # Vérifie que la description a été mise à jour