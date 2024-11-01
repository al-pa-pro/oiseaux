
from tests.client import *

def test_accueil(client):
    """
    Teste la route d'accueil.
    """
    response = client.get('/')  # Effectue une requête GET sur la route d'accueil
    assert response.status_code == 200  # Vérifie que la réponse est un code 200 (OK)
    assert b'Pourquoi les Oiseaux Sont-Ils Si Mignons ?' in response.data  # Vérifie que le contenu de la réponse contient 'index'

def test_formulaire(authenticated_client):
    """
    Teste la route du formulaire.
    """
    response = authenticated_client.get('/formulaire')  # Effectue une requête GET sur la route du formulaire
    assert response.status_code == 200  # Vérifie que la réponse est un code 200 (OK)
    assert b'Soumettre un Oiseau' in response.data  # Vérifie que le contenu de la réponse contient 'formulaire'

