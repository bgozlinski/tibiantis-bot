"""
Tibiantis Online Scraper
========================

Module providing functionality for scraping data from Tibiantis Online server (https://tibiantis.online/).
Allows retrieving information about player characters.
"""



from typing import Optional, Dict
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class TibiantisScraper:
    """
    A class implementing scraping functionality for Tibiantis Online server.

    Attributes:
        base_url (str): Base URL of the Tibiantis Online server

    Example:
        scraper = TibiantisScraper()
        character_data = scraper.get_character_data("Karius")
    """

    def __init__(self):
        """Initialize scraper instance with base URL."""
        self.base_url = "https://tibiantis.online/"

    def get_character_data(self, character_name: str) -> Optional[Dict]:
        """
        Retrieve character information from Tibiantis Online.

        Parameters:
            character_name (str): Name of the character to search for

        Returns:
            Optional[Dict]: Dictionary containing character data or None if an error occurs.
                          The dictionary may include the following keys:
                          - name (str): Character name
                          - sex (str): Character gender
                          - vocation (str): Character vocation
                          - level (str): Character level
                          - world (str): Game world
                          - residence (str): City of residence
                          - last_login (str): Last login date
                          - account_status (str): Account status

        Example:
            def get_character_info():
                scraper = TibiantisScraper()
                return scraper.get_character_data("Karius")
        """

        try:
            search_url = f"{self.base_url}?page=character&name={character_name}"
            response = requests.get(search_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            character_data = {}

            rows = soup.find_all("tr", class_="hover")
            if not rows:
                logger.warning(f"No data found for character: {character_name}")
                return None

            for row in rows:
                cols = row.find_all("td")
                key = cols[0].text.strip().lower().replace(' ', '_')
                value = cols[1].text.strip()
                character_data[key] = value

            return character_data


        except requests.RequestException as e:
            logger.error(f"Error fetching data for {character_name}: {e}")
            return None
