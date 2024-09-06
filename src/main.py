"""Project used for scraping bolivian banks."""
from src.scrapers import scraper_bnb, scraper_bcp, scraper_bg,scraper_bu


def main():
    """Main function."""

        # Ejecuta los scrapers
    scraper_bnb.scrap()
    scraper_bcp.scrap()
    scraper_bg.scrap()
    scraper_bu.scrap()

if __name__ == "__main__":
    main()