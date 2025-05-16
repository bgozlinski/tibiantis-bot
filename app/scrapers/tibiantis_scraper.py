"""
Tibiantis Online Scraper
========================

Module providing functionality for scraping data from Tibiantis Online server (https://tibiantis.online/).
Allows retrieving information about player characters.
"""
from typing import Optional, Dict, List, Any
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from dateutil import parser
from app.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class TibiantisScraper(BaseScraper):
    """
    A class implementing scraping functionality for Tibiantis Online server.

    Attributes:
        base_url (str): Base URL of the Tibiantis Online server

    Example:
        scraper = TibiantisScraper()
        character_data = scraper.get_character_data("Karius")
    """

    def __init__(self):
        """Initialize a scraper instance with base URL."""
        super().__init__("https://tibiantis.online/")

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
        logger.info(f"Scraping character data for: {character_name}")

        try:
            search_url = f"{self.base_url}?page=character&name={character_name}"
            soup = self.scrape_page(search_url)

            if not soup:
                return None

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
                        tzinfos = {
                            "CEST": 7200,   # UTC+2
                            "CET": 3600     # UTC+1
                        }

                        logger.debug(f"Parsing last_login date: {value}")
                        try:
                            parsed_date = parser.parse(value, tzinfos=tzinfos)
                            value = datetime(
                                parsed_date.year,
                                parsed_date.month,
                                parsed_date.day,
                                parsed_date.hour,
                                parsed_date.minute,
                                parsed_date.second,
                                tzinfo=None
                            )
                            logger.debug(f"Successfully parsed last_login date: {value}")
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Could not parse last_login date: {value}. Error: {e}")
                            value = None

                    elif field_name == 'level':
                        logger.debug(f"Parsing level value: {value}")
                        try:
                            value = int(value)
                            logger.debug(f"Successfully parsed level: {value}")
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Could not parse level value: {value}. Error: {e}")
                            value = None

                    character_data[field_name] = value

            logger.info(f"Successfully scraped data for character: {character_name}")
            logger.debug(f"Scraped fields: {list(character_data.keys())}")
            return character_data

        except requests.RequestException as e:
            logger.error(f"Error fetching data for {character_name}: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error while scraping data for {character_name}: {e}", exc_info=True)
            return None

    def get_online_players(self, min_level: int = 0) -> List[Dict]:
        """
        Retrieve a list of online players from Tibiantis Online.

        Parameters:
            min_level (int): Minimum level threshold for filtering players

        Returns:
            List[Dict]: List of dictionaries containing player data
        """
        logger.info(f"Scraping online players with minimum level {min_level}")

        url = f"{self.base_url}?page=whoisonline"
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
        table = soup.find("table", class_="tabi")

        if not table:
            logger.warning("No data found for online players")
            return []

        rows = table.find_all("tr")[2:]  # Skip header rows

        for row in rows:
            cols = row.find_all("td")
            try:
                name = extract_name(cols[0])
                level = extract_level(cols[2])

                if level >= min_level:
                    online_players.append({
                        "name": name,
                        "level": level
                    })

            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse player data: {e}")
                continue

        return online_players

    def _parse_death_data(self, soup: BeautifulSoup, character_name: str) -> List[Dict]:
        """
        Parse death data from a BeautifulSoup object.

        Parameters:
            soup (BeautifulSoup): BeautifulSoup object containing the HTML
            character_name (str): Name of the character

        Returns:
            List[Dict]: List of death entries
        """
        try:
            tables = soup.find_all("table", class_="tabi")

            # Check if we have enough tables and if the second table contains death information
            if len(tables) < 2 or "Latest Deaths" not in tables[1].text:
                logger.info(f"No death information found for character: {character_name}")
                return []

            deaths_list = []
            rows = tables[1].find_all("tr")[1:]  # Skip header row

            for row in rows:
                cols = row.find_all("td")
                time_str = cols[0].text.strip()
                killer_str = cols[1].text.strip()

                # Parse the date
                try:
                    tzinfos = {"CEST": 7200, "CET": 3600}
                    time = parser.parse(time_str, tzinfos=tzinfos)
                except (ValueError, TypeError):
                    time = None

                deaths_list.append({
                    "time": time,
                    "killer": killer_str,
                })

            return deaths_list

        except Exception as e:
            logger.error(f"Error parsing death data for {character_name}: {e}", exc_info=True)
            return []

    def get_character_deaths(self, character_name: str) -> List[Dict]:
        """
        Retrieve character death information from Tibiantis Online.

        Parameters:
            character_name (str): Name of the character to check

        Returns:
            List[Dict]: List of death entries, each containing:
                - time (datetime): When the death occurred
                - killer (str): Name of the killer
        """
        logger.info(f"Scraping death data for: {character_name}")

        search_url = f"{self.base_url}?page=character&name={character_name}"
        soup = self.scrape_page(search_url)

        if not soup:
            return []

        return self._parse_death_data(soup, character_name)

    async def get_character_deaths_async(self, character_name: str) -> List[Dict]:
        """
        Asynchronous version of get_character_deaths.
        Retrieve character death information from Tibiantis Online.

        Parameters:
            character_name (str): Name of the character to check

        Returns:
            List[Dict]: List of death entries, each containing:
                - time (datetime): When the death occurred
                - killer (str): Name of the killer
        """
        import httpx

        logger.info(f"Asynchronously scraping death data for: {character_name}")

        try:
            search_url = f"{self.base_url}?page=character&name={character_name}"

            async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
                response = await client.get(search_url)
                response.raise_for_status()

            soup = self.parse_html(response.text)

            if not soup:
                return []

            return self._parse_death_data(soup, character_name)

        except Exception as e:
            logger.error(f"Error fetching death data for {character_name}: {e}", exc_info=True)
            return []
