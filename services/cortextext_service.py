import sys
import os
import logging
import requests
import json
import html
from dotenv import load_dotenv


# Importer les variables d'environnement
load_dotenv()  # Charge les variables d'environnement depuis le fichier .env
CORTEX_API_KEY = os.getenv("CORTEX_API_KEY")

# Configuration de base du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Chemin vers le dossier parent
dossier_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dossier_parent)

def generate_description(prompt):
    """Génère une description d'oiseau à partir d'un prompt en utilisant l'API Cortex."""
    url = 'https://api.textcortex.com/v1/texts/blogs'
    
    data = {
        "context": prompt,
        "formality": "default",
        "keywords": ["oiseau", "nature"],
        "max_tokens": 400,
        "model": "claude-3-haiku",
        "n": 1,
        "source_lang": "fr",
        "target_lang": "fr",
        "temperature": 0.7,
        "title": "oiseau"
    }

    headers = {
        'Authorization': f'Bearer {CORTEX_API_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))

        # Vérification de la réponse de l'API
        if response.status_code == 200:
            generated_text = response.json()
            description = generated_text['data']['outputs'][0]['text']
            logging.info("Description générée avec succès.")
            return description
        else:
            logging.error("Erreur lors de la génération du texte : %s", response.status_code)
            logging.error("Détails de l'erreur : %s", response.text)
            return None
    except requests.exceptions.RequestException as e:
        logging.error("Erreur de requête : %s", str(e))
        return None

# Exemple d'utilisation de la fonction
if __name__ == "__main__":
    prompt = "Décris les caractéristiques uniques du corbeau."
    description = generate_description(prompt)
    if description:
        print("Texte formaté pour la base de données :\n")
        print(description)
