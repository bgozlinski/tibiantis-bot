from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import logging
from app.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class TibiantisInfoScraper(BaseScraper):
    """
    A class implementing scraping functionality for Tibiantis Info site.

    Attributes:
        base_url (str): Base URL of the Tibiantis Info site

    Example:
        scraper = TibiantisInfoScraper()
        online_players = scraper.get_online_players(min_level=50)
    """

    def __init__(self):
        """Initialize a scraper instance with base URL."""
        super().__init__("https://tibiantis.info/")

    def get_online_players(self, min_level: int = 0) -> List[Dict]:
        """
        Retrieve a list of online players from Tibiantis Info site.

        Parameters:
            min_level (int): Minimum level threshold for filtering players

        Returns:
            List[Dict]: List of dictionaries containing player data
        """
        logger.info(f"Scraping online players with minimum level {min_level}")

        url = f"{self.base_url}stats/online"
        soup = self.scrape_page(url)

        if not soup:
            return []

        # Define extractors for the table columns
        def extract_name(col):
            return col.find("a").text.strip()

        def extract_level(col):
            return int(col.text.strip())

        # Extract data from the table
        online_players = []
        table = soup.find("table", class_="mytab long")

        if not table:
            logger.warning("No data found for online players")
            return []

        rows = table.find_all("tr")[3:]  # Skip header rows

        for row in rows:
            cols = row.find_all("td")
            try:
                name = extract_name(cols[1])
                level = extract_level(cols[4])

                if level >= min_level:
                    online_players.append({
                        "name": name,
                        "level": level
                    })

            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse player data: {e}")
                continue

        return online_players
