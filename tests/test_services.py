from tests.client import *


def test_get_db_connection_in_memory(app):
    """Test de la connexion à la base de données en mémoire."""
    with app.app_context():
        conn = get_sqlite_connection()
        assert conn is not None  # Vérifie que la connexion n'est pas None
        cursor = conn.execute('SELECT sqlite_version();')
        version = cursor.fetchone()[0]
        assert version is not None  # Vérifie que la version SQLite a été récupérée
        assert version == sqlite3.sqlite_version  # Vérifie que la version correspond à la version SQLite

def test_get_db_connection_on_disk(app):
    """Test de la connexion à la base de données sur disque."""
    app.config['TESTING'] = False  # Désactive le mode test
    with app.app_context():
        conn = get_sqlite_connection()
        assert conn is not None  # Vérifie que la connexion n'est pas None
        cursor = conn.execute('SELECT sqlite_version();')
        version = cursor.fetchone()[0]
        assert version is not None  # Vérifie que la version SQLite a été récupérée
        assert version == sqlite3.sqlite_version  # Vérifie que la version correspond à la version SQLite



@pytest.fixture
def mock_file(mocker):
    # Créer un mock pour le fichier
    file = FileStorage(stream=b"file content", filename="test.png")
    return file

def test_save_file(mocker, mock_file):
    # Mock de os.path.join pour éviter d'accéder au système de fichiers
    mocker.patch("os.path.join", return_value="mock_path/test.png")
    
    # Mock de la méthode save pour le fichier
    mock_save = mocker.patch.object(mock_file, 'save', autospec=True)
    
    # Appeler la fonction avec le fichier mocké
    result = save_file(mock_file, "mock_path")
    
    # Vérifier que le bon fichier est renvoyé
    assert result == "test.png"
    
    # Vérifier que la méthode save a été appelée avec le bon chemin
    mock_save.assert_called_once_with("mock_path/test.png")



#test des models


def test_load_user(client):
    User1=load_user(1)
    expected_value=(1,'pili',pw,"user")
    value=(User1.id,User1.username,User1.password,User1.role)
    assert value==expected_value
    User2=load_user(2)
    assert User2==None


#test init_admin

def test_ajouter_admin(app):
    """Test pour ajouter un administrateur."""
    # Vérifier que l'administrateur n'est pas présent au début
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = 'kiwi' AND role ='admin'" )
    assert cursor.fetchone() is None  # L'utilisateur ne devrait pas exister

    # Appelle la fonction pour ajouter l'administrateur
    ajouter_admin()

    # Vérifie que l'administrateur a été ajouté
    cursor.execute("SELECT * FROM users WHERE username = 'kiwi'")
    admin = cursor.fetchone()
    assert admin is not None  # L'utilisateur devrait exister
    assert admin[3] == 'admin'  # Vérifie que le rôle est 'admin'
    assert check_password_hash(admin[2], 'kiwi')  # Vérifie que le mot de passe est correct (hashé)

    conn.close()

def test_ajouter_admin_existant(app):
    """Test pour vérifier que l'administrateur n'est pas ajouté s'il existe déjà."""
    # Ajoute un utilisateur admin au départ
    ajouter_admin()

    # Vérifie que l'administrateur existe déjà
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'kiwi'")
    count_before = cursor.fetchone()[0]

    # Appelle la fonction pour ajouter l'administrateur à nouveau
    ajouter_admin()

    # Vérifie que le nombre d'utilisateurs 'kiwi' n'a pas changé
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'kiwi'")
    count_after = cursor.fetchone()[0]

    assert count_before == count_after  # Le nombre d'utilisateurs ne doit pas avoir changé
    conn.close()