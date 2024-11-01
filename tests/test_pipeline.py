from tests.client import *

BASE_URL = 'https://api.ebird.org/v2/data/obs/geo/recent'


locations = [
    {'lat': 6.5244, 'lng': 3.3792, 'dist': 50, 'name': 'Lagos, Nigeria'},
    {'lat': 9.0579, 'lng': 7.49508, 'dist': 50, 'name': 'Abuja, Nigeria'},
]



def test_api_data_retrieval():
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"speciesCode": "ABC", "comName": "Mock Bird", "sciName": "Mockus Birdus", "obsDt": "2023-10-19T12:00:00Z", "howMany": 2, "lat": 6.5244, "lng": 3.3792}
    ]
    
    with mock.patch('requests.get', return_value=mock_response):
        all_data = []
        for loc in locations:
            params = {'lat': loc['lat'], 'lng': loc['lng'], 'dist': loc['dist']}
            headers = {'X-eBirdApiToken': EBIRD_API_KEY}
            response = requests.get(BASE_URL, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data)
                df['location'] = loc['name']
                all_data.append(df)
        
        final_df = pd.concat(all_data, ignore_index=True)
        assert len(final_df) == len(locations)  # Assurer que 1 ligne de données a été récupérée
        assert final_df.iloc[0]['speciesCode'] == "ABC"  # Vérifier que les données sont correctes

def test_remove_duplicates():
    # Création d'un DataFrame avec des doublons
    data = {
        "speciesCode": ["ABC", "ABC", "DEF"],
        "obsDt": ["2023-10-19T12:00:00Z", "2023-10-19T12:00:00Z", "2023-10-19T12:00:00Z"],
        "location": ["Lagos, Nigeria", "Lagos, Nigeria", "Abuja, Nigeria"]
    }
    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=['speciesCode', 'obsDt', 'location'])
    
    assert len(df) == 2  # Vérifier que le nombre de lignes a diminué de 3 à 2
    assert df.iloc[0]['speciesCode'] == "ABC"  # Vérifier que le premier enregistrement est correct



