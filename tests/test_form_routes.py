from tests.client import *



def test_soumettre(authenticated_client):
    # Simuler une requête POST à la route /soumettre
    response = authenticated_client.post('/soumettre', data={
        'nom': 'Oiseau Test',
        'nom_scientifique':'oiseau scientifique',
        'code':'code test',
        'description': 'Une description de test.',
        'audio':  'test_audio.mp3',
        'video': 'test_video.mp4',
        'images': 
           'test_image.jpg'
        
    })

    # Vérifier que la redirection se fait vers la racine
    assert response.status_code == 302
    assert response.location == '/'  # Vérifiez que la redirection se fait vers la racine

def test_soumettre_sans_fichiers(authenticated_client):
    # Simuler une requête POST à la route /soumettre sans fichiers
    response = authenticated_client.post('/soumettre', data={
        'nom': 'Oiseau Test Sans Fichiers','nom_scientifique':'oiseau scientifique sans fichier','code':'code sans fichier',
        'description': 'Une description de test sans fichiers.'
    })

    # Vérifier que la redirection se fait vers la racine
    assert response.status_code == 302
    assert response.location == '/'  # Vérifiez que la redirection se fait vers la racine
