from tests.client import *


def test_signup(client):
    """Test de l'inscription."""
    response = client.post('/signup', data={
        'username': 'Martin-pêcheur',
        'password': 'motdepasse123'
    }, follow_redirects=True)

    # Vérifie que la réponse contient un message de succès
    assert b'Inscription reussie' in response.data

    # Vérifie que l'utilisateur est bien créé dans la base de données
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", ('Martin-pêcheur',))
    user = cursor.fetchone()
    assert user is not None
    assert user[1] == 'Martin-pêcheur'
    conn.close()

def test_login(client):
    """Test de la connexion."""
    # Prépare l'utilisateur dans la base de données de test
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?,?, 'user')",('Aigle', generate_password_hash('hashed_password')))
    conn.commit()
    conn.close()

    # Teste la connexion
    response = client.post('/login', data={
        'username': 'Aigle',
        'password': 'hashed_password'
    }, follow_redirects=True)

    # Vérifie que la connexion réussie redirige vers le dashboard (ou une autre page)
    assert response.status_code == 200
    assert b'Tableau de bord' in response.data  # Remplace 'Dashboard' par la page à laquelle on est redirigé après login

def test_login_fail(client):
    """Test de l'échec de connexion avec des informations incorrectes."""
    response = client.post('/login', data={
        'username': 'Oiseau-inexistant',
        'password': 'mauvais_motdepasse'
    }, follow_redirects=True)

    # Vérifie que la connexion échoue et affiche un message d'erreur
    assert b'Nom d utilisateur ou mot de passe incorrect' in response.data

def test_logout(client):
    """Test de la déconnexion."""
    # Prépare l'utilisateur et connecte-le
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?,?, 'user')",('Aigle', generate_password_hash('hashed_password')))
    conn.commit()
    conn.close()

    # Connexion
    client.post('/login', data={
        'username': 'Aigle',
        'password': 'hashed_password'
    }, follow_redirects=True)

    # Teste la déconnexion
    response = client.get('/logout', follow_redirects=True)

    # Vérifie que l'utilisateur est déconnecté
    assert b'Vous avez ete deconnecte' in response.data  # Si un message de déconnexion est prévu
    assert response.status_code == 200