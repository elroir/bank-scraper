"""Scraper for Banco Bisa"""
import re
import requests
from bs4 import BeautifulSoup
from src.uploader import post_data_to_api, get_bank_id

def extract_first_limit_info(text):
    """Extracts the first limit information from the given text."""
    
    # Patrones para buscar el primer límite (agregamos más variaciones)
    patterns = [
        r"límite (\w+) de (USD|Bs\.|u\$)\s*(\d+)",
        r"límite de (USD|Bs\.|u\$)\s*(\d+) (\w+)",
        r"hasta un límite (\w+) de (USD|Bs\.|u\$)\s*(\d+)"
    ]
    bank_id = get_bank_id("BISA")
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                if groups[0].lower() in ['usd', 'bs.', 'u$']:
                    currency, amount, frequency = groups
                else:
                    frequency, currency, amount = groups
                return {
                    "description": "compras por internet, POS, y retiros ATM",
                    "frequency": frequency.lower(),
                    "currency": currency.upper() if currency.lower() != "u$" else "USD",
                    "card_type": "debit",
                    "bank": bank_id,
                    "amount": int(amount),
                    "number": 1,
                    "extra" : text
                }
    
    print("No se encontró coincidencia con ningún patrón.")
    return None

def scrap():
    """Scrapes the BISA tariff table and uploads the data to the API."""
    # URL de la página web
    url = "https://www.bisa.com/bisa-efectiva"

    # Obtener el contenido de la página web
    response = requests.get(url,timeout=10)
    html_content = response.text

    # Crear objeto BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Buscar el elemento <li> que comienza con el texto deseado
    target_li = soup.find('li', string=lambda text: text and text.strip().startswith('Realizar compras en POS en el exterior'))

    if target_li:
        text = target_li.text.strip()
        limit_info = extract_first_limit_info(text)

        if limit_info:
            post_data_to_api([limit_info])
        else:
            print("No se encontró información de límite en el texto.")
    else:
        print("No se encontró el elemento deseado.")