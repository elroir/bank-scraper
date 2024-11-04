"""This module contains the scraper for Banco Ganadero's PDF tariff table."""
import re
import io
import pdfplumber
import requests
from src.uploader import post_data_to_api, get_bank_id

def extract_info(text):
    """Extracts the information from the PDF text."""
    pattern = r'(.*?) hasta USD (\d+) por (\w+)'
    matches = re.findall(pattern, text)


    bank_id = get_bank_id('BG')
    results = []
    number = 0
    for match in matches:
        number += 1
        results.append({
            'description': match[0].replace('-', ' ').strip(),
            'frequency': match[2],
            'currency' : 'USD',
            'card_type': 'debit',
            'bank': bank_id,
            'number': number,
            'amount': match[1]
        })

    return results

def scrap():
    """Scrapes the PDF tariff table and prints the extracted information as JSON."""
    # URL of the remote PDF
    pdf_url = 'https://prodbgwebportal.blob.core.windows.net/assets/pdf-tarifario.pdf'

    # Download the PDF
    response = requests.get(pdf_url, timeout=10)
    pdf_file = io.BytesIO(response.content)

    # Open the PDF from the BytesIO object
    with pdfplumber.open(pdf_file) as pdf:
        # Get page 46 (index 45 since pdfplumber uses 0-based indexing)
        page = pdf.pages[45]

        # Extract text from the page
        text = page.extract_text()

        # Extract the information
        info = extract_info(text)
        
        post_data_to_api(info)