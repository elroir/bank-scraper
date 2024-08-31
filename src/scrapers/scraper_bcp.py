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
        found_4_1_6 = False

        # Recorrer todas las filas una sola vez
        for tr in table.find_all('tr'):
            text = tr.text.strip()
            normalized_text = text.replace('\xa0', ' ').strip()  # Normaliza el texto reemplazando caracteres no visibles
            if normalized_text.startswith('4'):
                # Guardar la fila según su identificador
                key = normalized_text.split('\n')[0].strip()
                data_points[key] = normalized_text.split('\n')
                if key == '4.1.6.':
                    found_4_1_6 = True
            elif found_4_1_6 and not normalized_text.startswith('4'):
                # Esta es la línea sin numeración después de 4.1.6.
                data_points['unnumbered_after_4_1_6'] = normalized_text.split('\n')
                break 
        # Extraer los títulos y los puntos específicos
        # column_titles = data_points.get('4.', [])
        point_4_1_3 = data_points.get('4.1.3.', [])
        point_4_1_4 = data_points.get('4.1.4', [])
        unnumbered_point = data_points.get('unnumbered_after_4_1_6', [])



        data = [
            {
                "description": point_4_1_3[1],
                "frequency": point_4_1_3[5],
                "currency": point_4_1_3[3],
                "card_type": "debit",
                "bank": bank_id,
                "amount": point_4_1_3[4]
            },
            {
                "description": point_4_1_4[1],
                "frequency": point_4_1_4[5],
                "currency": point_4_1_4[3],
                "card_type": "debit",
                "bank": bank_id,
                "amount": point_4_1_4[4]
            },
            {
                "description": unnumbered_point[0],
                "frequency": unnumbered_point[4] if len(unnumbered_point) > 4 else "",
                "currency": unnumbered_point[2] if len(unnumbered_point) > 2 else "",
                "card_type": "debit",
                "bank": bank_id,
                "amount": unnumbered_point[3] if len(unnumbered_point) > 3 else ""
            }
        ]

        post_data_to_api(data)