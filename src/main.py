"""Project used for scraping bolivian banks."""
from dotenv import load_dotenv

from src.scrapers import scraper_bnb, scraper_bisa, scraper_bcp, scraper_bg,scraper_bu,scraper_eco

def main():
    """Main function."""
    load_dotenv()

        # Ejecuta los scrapers
    scraper_bnb.scrap()
    scraper_bcp.scrap()
    scraper_bg.scrap()
    scraper_bu.scrap()
    scraper_bisa.scrap()
    scraper_eco.scrap()
    

if __name__ == "__main__":
    main()