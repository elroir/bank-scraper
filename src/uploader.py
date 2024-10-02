"""This module contains the functions to upload the data to the API."""
import os

import requests
def post_data_to_api(data):
    """Posts the data to the API."""
    api_url = f"{os.getenv('API_URL')}/collections/card_restriction/records"
    headers = {
            "api-key"     : os.getenv('API_KEY'),
            "Content-Type": "application/json"
        }

    for item in data:
        response = requests.post(api_url, json=item, headers=headers, timeout=10)

        if response.status_code == 200 or response.status_code == 201:
            print(f"Dato guardado exitosamente: {item['description']}")
        else:
            print(f"Error al guardar el dato: {item['description']}")
            print("Código de estado:", response.status_code)
            print("Respuesta:", response.text)

def get_bank_id(bank_code):
    """Gets the bank ID from the API."""
    bank_url = f"https://pb.elroir.cloud/api/collections/bank/records?filter=(code='{bank_code}')"
    response = requests.get(bank_url,timeout=10)
    bank_id = response.json()["items"][0]["id"]
    return bank_id
