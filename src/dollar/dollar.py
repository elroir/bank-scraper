"""This module retrieves data from criptoya.com and uploades to server"""
import os

import requests

def get_crypto_dollar(dollar_id):
    """gets info from crypto provider"""
    api_url = f"{os.getenv('CRYPTO_API')}/binancep2p/usdt/BOB/1"
    response = requests.get(api_url,timeout=10)
    data = {
        "sell_price"  : response.json()["ask"],
        "buy_price"   : response.json()["bid"],
        "dollar_type" : dollar_id,
        "user_source" : "admin"
        }
    return data

def get_dollar_id(name_en,dollars):
    """gets dollar id from list with dollar english name"""
    dollar_ids = list(filter(lambda x: x['name_en'] == name_en, dollars))
    return dollar_ids[0]['id'] if dollar_ids else None

def upoad_dollar():
    """Uploads to dollar crypto"""
    crypto_url = f"{os.getenv('API_URL')}/collections/dollar_crypto/records"
    headers = {
            "api-key"     : os.getenv('API_KEY'),
            "Content-Type": "application/json"
        }
    response = requests.get(crypto_url,headers=headers,timeout=10)
    dollars = response.json()['items']
    crypto_id = get_dollar_id(name_en='Crypto',dollars=dollars)
    crypto_dollar = get_crypto_dollar(dollar_id=crypto_id)
    parallel_id = get_dollar_id(name_en='Parallel',dollars=dollars)
    parallel_dollar = crypto_dollar | {'dollar_type': parallel_id}
    data = [crypto_dollar,parallel_dollar]
    api_url = f"{os.getenv('API_URL')}/collections/dollar/records"
    for dollar in data:
        response = requests.post(api_url,json=dollar,headers=headers,timeout=10)
        print(response.json())


if __name__ == '__main__':
    upoad_dollar()