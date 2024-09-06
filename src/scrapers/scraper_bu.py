"""Scraper for banco Unión."""

import re
import io
import requests
import pdfplumber
from src.uploader import post_data_to_api, get_bank_id


def parse_line(line,number):
    """Parse a line from the tariff table and return a dictionary with the data."""
    frequencies = ["quincenal", "diario", "mensual", "semanal"]
    
    # Dividir la línea en palabras, ignorando espacios extras
    parts = re.findall(r'\S+', line)
    bank_id = get_bank_id("BU")
    
    # Buscar la frecuencia en la línea
    frequency = None
    freq_index = -1
    for i, part in enumerate(parts):
        if part.lower() in frequencies:
            frequency = part.lower()
            freq_index = i
            break
    
    if frequency:
        description = " ".join(parts[:freq_index])
        currency = parts[-2] if len(parts) >= 2 else ""
        amount = parts[-1] if parts else ""
    else:
        # Si no se encuentra la frecuencia, asumimos que está al final
        description = " ".join(parts[:-3]) if len(parts) >= 3 else ""
        frequency = parts[-3].lower() if len(parts) >= 3 else ""
        currency = parts[-2] if len(parts) >= 2 else ""
        amount = parts[-1] if parts else ""
    
    # Limpia la moneda de posibles puntos
    currency = currency.rstrip('.')
    
    return {
        "description": description.strip(),
        "frequency": frequency,
        "currency": currency,
        "card_type": "debit",
        "bank": bank_id,
        "number": number,
        "amount": amount
    }

def scrap():
    """Scrapes the BU tariff table and uploads the data to"""
    # URL del PDF
    url = "https://bancounion.com.bo/PDF/TasasTarifario/Tarifario_Servicios-2024_08_v2.pdf"

    # Descarga el PDF
    response = requests.get(url, timeout=10)
    pdf_file = io.BytesIO(response.content)

    # Abre el archivo PDF desde el objeto BytesIO
    with pdfplumber.open(pdf_file) as pdf:
        # Busca en todas las páginas
        target_data = None
        number = 0
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row and isinstance(row[0], str) and re.search(r'(Consumos en POS|Pagos por Internet|Retiros en ATM)', row[0]):
                        target_data = row[0]
                        break
                if target_data:
                    break
            if target_data:
                break

        if target_data:
            # Divide la cadena en líneas
            lines = target_data.split('\n')
            result = []

            # Procesa cada línea y crea un diccionario
            for line in lines:
                number+=1
                result.append(parse_line(line,number))
            
            post_data_to_api(result)
        else:
            print("No se encontraron los datos esperados.")