from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class TibiantisInfoScraper:
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
        self.base_url = "https://tibiantis.info/"

    def get_online_players(self, min_level: int = 0) -> List[Dict]:
        logger.info(f"Scraping online players with minimu level {min_level}")

        try:
            url = f"{self.base_url}stats/online"
            logger.debug(f"Requesting URL: {url}")

            response = requests.get(url)
            response.raise_for_status()
            logger.debug(f"Received response with status code: {response.status_code}")

            soup = BeautifulSoup(response.text, "html.parser")

            table = soup.find("table", class_="mytab long")

            if not table:
                logger.warning("No data found for online players")
                return []

            rows = table.find_all("tr")
            if not rows:
                logger.warning("No data found for online players")
                return []

            online_players = []
            rows = table.find_all("tr")[3:]

            for row in rows:
                cols = row.find_all("td")
                try:
                    name = cols[1].find("a").text.strip()
                    level = cols[4].text.strip()

                    if int(level) >= min_level:
                        online_players.append({
                            "name": name,
                            "level": level
                        })

                except (ValueError, IndexError) as e:
                    logger.warning(f"Could not parse player data: {e}")
                    continue

            return online_players

        except requests.RequestException as e:
            logger.error(f"Error fetching data for online players: {e}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Unexpected error while scraping data for online players: {e}", exc_info=True)
            return []
