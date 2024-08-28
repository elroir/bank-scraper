"""Scraper for BNB tariff table."""


import io
import re
import pdfplumber
import requests


from src.uploader import post_data_to_api, get_bank_id

def scrap():
    """Scrapes the BNB tariff PDF and uploads the data to the API."""

    url = "https://www.bnb.com.bo/PortalBNB/Documentos/Tarifario/TarifarioNormaSCLIE.pdf"
    response = requests.get(url,timeout=10)

    with pdfplumber.open(io.BytesIO(response.content)) as pdf:
        target_page = pdf.pages[3]  # Page 4 is index 3
        text = target_page.extract_text()

        # Extract table data
        table_data = []
        lines = text.split('\n')

        bank_id = get_bank_id("BNB")
        for line in lines:
            if line.startswith('5.14.'):
                # Use regex to separate description from the rest
                match = re.match(r'(5\.14\.\S+\s*.*?)\s+(\S+)\s+(\S+)$', line)
                if match:
                    description = match.group(1).strip()
                    currency = match.group(2)
                    amount = match.group(3)

                    # Remove only numbers and dots at the beginning of the description
                    description = re.sub(r'^5\.14\.\d+\s*', '', description)

                    # Convert amount to float, removing any non-numeric characters except '.'
                    amount = re.sub(r'[^\d.]', '', amount)
                    try:
                        amount = float(amount)
                    except ValueError:
                        print(f"Could not convert amount to float: {amount}")
                        amount = 0.0  # or None, depending on how you want to handle this case

                    table_data.append({
                        "description": description,
                        "currency": currency,
                        "card_type": "debit",
                        "amount": amount,
                        "bank": bank_id
                    })

        post_data_to_api(table_data)
