"""Scraper for banco Economico."""

import io
import requests
import pdfplumber
from src.uploader import post_data_to_api, get_bank_id

def download_and_extract_table(url):
    """Extracts required table"""

    # Descargar el PDF
    response = requests.get(url,timeout=10)
    pdf_file = io.BytesIO(response.content)
    
    # Extraer tabla con pdfplumber
    with pdfplumber.open(pdf_file) as pdf:
        page = pdf.pages[11]  # página 12 (índice 11)
        tables = page.extract_tables()
        return tables



def scrap():
    """Looks for data at url"""
    result = []
    bank_id = get_bank_id("ECO")
    url = "https://www.baneco.com.bo/assets/content/docs/footers/tarifario/Tarifario_Comisiones_Productos_y_Servicios-0242.pdf"

    table_data = download_and_extract_table(url)
    
    # Buscamos la fila que contiene "Compras Online" y "Compras Presencial"
    for row in table_data[0]:  # Asumimos que es la primera tabla
        if isinstance(row, list):
            # Para Compras Online
            if any('Compras Online' in str(cell) for cell in row):
                online_amount = next((cell for cell in row if str(cell).isdigit()), None)
                if online_amount:
                    result.append({
                        "description": "Compras Online",
                        "frequency": "Mensual",
                        "currency": "Bs",
                        "card_type": "debit",
                        "bank": bank_id,
                        "amount": int(online_amount),
                        "number": 1
                    })
            
            # Para Compras Presencial
            if any('Compras Presencial' in str(cell) for cell in row):
                presencial_amount = next((cell for cell in row if str(cell).isdigit()), None)
                if presencial_amount:
                    result.append({
                        "description": "Compras Presencial",
                        "frequency": "Mensual",
                        "currency": "Bs",
                        "card_type": "debit",
                        "bank": bank_id,
                        "amount": int(presencial_amount),
                        "number": 2
                    })

    post_data_to_api(result)