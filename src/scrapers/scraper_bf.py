"""This module contains the scraper for Banco Fortaleza's PDF tariff table."""
import io

import pdfplumber
import requests
from src.uploader import post_data_to_api, get_bank_id

def download_and_extract_limits():
    """Downloads and formats data"""
    url = "https://www.bancofortaleza.com.bo/wp-content/uploads/2024/08/TARIFARIO-BFO-29-08-2024-v-17-2024.pdf"
    bank_id = get_bank_id("BF")
    
    try:
        response = requests.get(url,timeout=10)
        response.raise_for_status()
        
        pdf_file = io.BytesIO(response.content)
        
        with pdfplumber.open(pdf_file) as pdf:
            page = pdf.pages[4]
            tables = page.extract_tables()
            
            limits_data = []
            number = 1
            
            for table in tables:
                for i, row in enumerate(table):
                    if row and any('Límites para uso en el exterior' in str(cell) for cell in row):
                        for j in range(i+1, i+4):
                            if j < len(table):
                                tipo = table[j][0] if table[j][0] is not None else ''
                                limit = table[j][2] if table[j][2] is not None else ''
                                
                                # Procesar el string del límite
                                limit_parts = limit.split()
                                amount = float(limit_parts[1])  # Convertir el monto a float
                                frequency = ' '.join(limit_parts[3:])  # Obtener la frecuencia
                                
                                limit_dict = {
                                    "description": tipo.strip(),  # Mantenemos la descripción original
                                    "frequency": frequency,
                                    "currency": "Bs.",
                                    "card_type": "debit",
                                    "bank": bank_id,
                                    "amount": amount,
                                    "number": number
                                }
                                
                                limits_data.append(limit_dict)
                                number += 1
                                
                        return limits_data
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el PDF: {e}")
        return None
    except Exception as e:
        print(f"Error al procesar el PDF: {e}")
        return None

def scrap():
    """Executes the scrap code"""
    limits = download_and_extract_limits()
    post_data_to_api(limits)