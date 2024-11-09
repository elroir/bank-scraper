"""Scraper for BCP tariff table."""

import requests
from bs4 import BeautifulSoup
from src.uploader import post_data_to_api, get_bank_id

def scrap():
    """Scrapes the BCP tariff table and uploads the data to the API."""
    url = 'https://www.bcp.com.bo/Tarifario/Tarjetas_de_Debito_Tarifario'

    # Hacer la solicitud HTTP y obtener el contenido HTML
    response = requests.get(url, timeout=10)
    html_content = response.content

    # Crear un objeto BeautifulSoup para parsear el HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Encontrar la tabla 4 y extraer los títulos de las columnas
    table = soup.find('table', {'class': 'bcp_tabla_tarifa bcp_tabla_tarifa_strip'})
    if table:
        data_points = {}
        bank_id = get_bank_id("BCP")

        # Recorrer todas las filas una sola vez
        for tr in table.find_all('tr'):
            text = tr.text.strip()
            normalized_text = text.replace('\xa0', ' ').strip()  # Normaliza el texto reemplazando caracteres no visibles
            if normalized_text.startswith('4.1.4.'):
                # Guardar la fila según su identificador
                key = normalized_text.split('\n')[0].strip()
                data_points[key] = normalized_text.split('\n')
                print(data_points)
           
        # Extraer los títulos y los puntos específicos
        # column_titles = data_points.get('4.', [])
        point_4_1_4 = data_points.get('4.1.4.', [])
        extra = 'Servicio no disponible para cuentas abiertas a partir del 01/01/2023. Aplica el tipo de cambio utilizado por Visa Internacional.'


        data = [
            {
                "description": 'Compras físicas, por internet y retiros en ATM a nivel Internacional',
                "frequency": point_4_1_4[5],
                "currency": point_4_1_4[3],
                "card_type": "debit",
                "bank": bank_id,
                "number": 1,
                "amount": point_4_1_4[4],
                "extra" : extra
            }
            
        ]

        post_data_to_api(data)