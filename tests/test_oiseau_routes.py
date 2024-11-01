from tests.client import *



def test_liste_oiseaux(client):
    """Teste la route pour afficher la liste des oiseaux."""
    response = client.get('/liste_oiseaux')
    assert response.status_code == 200
    assert b'Rouge-gorge' in response.data
    assert b'Merle' not in response.data

def test_liste_propositions(admin_client):
    """Teste la route pour afficher la liste des oiseaux."""
    response = admin_client.get('/liste_propositions')
    assert response.status_code == 200
    assert b'Merle' in response.data
    assert b'Rouge-gorge' not in response.data

def test_afficher_oiseau(client):
    """Teste la route pour afficher un oiseau spécifique."""
    response = client.get('/oiseau/1')
    assert response.status_code == 200
    assert b'Rouge-gorge' in response.data

    # Test pour un oiseau non existant
    response = client.get('/oiseau/999')
    assert response.status_code == 404
    assert b'Oiseau non trouve' in response.data

def test_supprimer_oiseau(admin_client):
    """Teste la route pour supprimer un oiseau."""
    
    # Vérifiez d'abord que l'oiseau existe avant la suppression
    response = admin_client.get('/liste_oiseaux')
    assert b'Rouge-gorge' in response.data  # Vérifiez que l'oiseau est présent

    # Supprimez l'oiseau
    response = admin_client.post('/supprimer_oiseau/1')
    assert response.status_code == 302  # Vérification de la redirection après suppression

    # Vérifiez que l'oiseau a été supprimé
    response = admin_client.get('/liste_oiseaux')
    assert b'Rouge-gorge' not in response.data  # Vérifiez que l'oiseau a été supprimé

def test_supprimer_oiseau_non_admin(authenticated_client):
    """Teste la route pour supprimer un oiseau."""
    
    # Vérifiez d'abord que l'oiseau existe avant la suppression
    response = authenticated_client.get('/liste_oiseaux')
    assert b'Rouge-gorge' in response.data  # Vérifiez que l'oiseau est présent

    # Supprimez l'oiseau
    response = authenticated_client.post('/supprimer_oiseau/1')
    assert response.status_code == 302  # Vérification de la redirection après suppression

    # Vérifiez que l'oiseau a été supprimé
    response = authenticated_client.get('/liste_oiseaux')
    assert b'Rouge-gorge' in response.data  # Vérifiez que l'oiseau a été supprimé


def test_changer_edit_mode(authenticated_client):
    # Vérifiez que le mode d'édition n'est pas activé par défaut
    with authenticated_client.session_transaction() as sess:
        sess['edit_mode'] = False 
        assert sess.get('edit_mode') is False
    


    # Appelez la route pour changer le mode d'édition
    response = authenticated_client.get('/changer_edit_mode/')  # Assurez-vous que l'URL correspond à votre route

    # Vérifiez que la redirection a eu lieu
    assert response.status_code == 302  # Redirection

    # Vérifiez que le mode d'édition est maintenant activé
    with authenticated_client.session_transaction() as sess:
        assert sess.get('edit_mode') is True

    # Appelez à nouveau la route pour changer le mode d'édition
    response = authenticated_client.get('/changer_edit_mode/')  # Assurez-vous que l'URL correspond à votre route

    # Vérifiez que le mode d'édition est maintenant désactivé
    with authenticated_client.session_transaction() as sess:
        assert sess.get('edit_mode') is False
