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
from datetime import datetime
from dateutil import parser

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
                          - house (str): House location (optional)
                          - guild_membership (str): Guild name (optional)
                          - last_login (str): Last login date
                          - comment (str): Character comment (optional)
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

            fields_to_scrape = {
                'name': 'name',
                'sex': 'sex',
                'vocation': 'vocation',
                'level': 'level',
                'world': 'world',
                'residence': 'residence',
                'house': 'house',
                'guild membership': 'guild_membership',
                'last login': 'last_login',
                'comment': 'comment',
                'account status': 'account_status'
            }

            rows = soup.find_all("tr", class_="hover")
            if not rows:
                logger.warning(f"No data found for character: {character_name}")
                return None

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 2:
                    continue

                key = cols[0].text.strip().lower().rstrip(':')
                value = cols[1].text.strip()

                if key in fields_to_scrape:
                    field_name = fields_to_scrape[key]

                    if field_name == 'last_login':
                        try:
                            parsed_date = parser.parse(value)
                            value = datetime(
                                parsed_date.year,
                                parsed_date.month,
                                parsed_date.day,
                                parsed_date.hour,
                                parsed_date.minute,
                                parsed_date.second
                            )
                        except (ValueError, TypeError):
                            logger.warning(f"Could not parse last_login date: {value}")
                            value = None

                    elif field_name == 'level':
                        try:
                            value = int(value)
                        except (ValueError, TypeError):
                            value = None

                    character_data[field_name] = value

            return character_data

        except requests.RequestException as e:
            logger.error(f"Error fetching data for {character_name}: {e}")
            return None

