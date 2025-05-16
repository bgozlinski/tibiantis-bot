import logging
import requests
from typing import Optional, Dict, List, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BaseScraper:
    """
    Base scraper class providing common web scraping functionality.
    
    This class serves as a foundation for specific scraper implementations,
    providing common methods for making HTTP requests, parsing HTML, and handling errors.
    
    Attributes:
        base_url (str): Base URL of the website to scrape
    """
    
    def __init__(self, base_url: str):
        """
        Initialize a scraper instance with base URL.
        
        Parameters:
            base_url (str): Base URL of the website to scrape
        """
        self.base_url = base_url
    
    def make_request(self, url: str,timeout: int = 10) -> Optional[requests.Response]:
        """
        Make an HTTP request to the specified URL.
        
        Parameters:
            url (str): URL to request
            
        Returns:
            Optional[requests.Response]: Response object or None if an error occurs
        """
        logger.debug(f"Requesting URL: {url}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            logger.debug(f"Received response with status code: {response.status_code}")
            return response
        except requests.RequestException as e:
            logger.error(f"Error fetching data from {url}: {e}", exc_info=True)
            return None
    
    def parse_html(self, html_content: str) -> Optional[BeautifulSoup]:
        """
        Parse HTML content using BeautifulSoup.
        
        Parameters:
            html_content (str): HTML content to parse
            
        Returns:
            Optional[BeautifulSoup]: BeautifulSoup object or None if an error occurs
        """
        try:
            return BeautifulSoup(html_content, "html.parser")
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}", exc_info=True)
            return None
    
    def scrape_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Make a request to a URL and parse the HTML content.
        
        Parameters:
            url (str): URL to scrape
            
        Returns:
            Optional[BeautifulSoup]: BeautifulSoup object or None if an error occurs
        """
        response = self.make_request(url)
        if not response:
            return None
        
        return self.parse_html(response.text)
    
    def extract_table_data(self, soup: BeautifulSoup, table_selector: str, 
                          row_start: int = 0, 
                          column_extractors: Dict[int, callable] = None) -> List[Dict[str, Any]]:
        """
        Extract data from an HTML table.
        
        Parameters:
            soup (BeautifulSoup): BeautifulSoup object containing the HTML
            table_selector (str): CSS selector for the table
            row_start (int): Index of the first row to extract (to skip headers)
            column_extractors (Dict[int, callable]): Dictionary mapping column indices to extraction functions
            
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing the extracted data
        """
        if column_extractors is None:
            column_extractors = {}
            
        result = []
        table = soup.select_one(table_selector)
        
        if not table:
            logger.warning(f"No table found with selector: {table_selector}")
            return result
        
        rows = table.find_all("tr")
        if len(rows) <= row_start:
            logger.warning(f"Table has fewer rows than row_start ({row_start})")
            return result
        
        for row in rows[row_start:]:
            cols = row.find_all("td")
            row_data = {}
            
            try:
                for col_idx, extractor in column_extractors.items():
                    if col_idx < len(cols):
                        row_data[extractor.__name__] = extractor(cols[col_idx])
                
                if row_data:
                    result.append(row_data)
            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse row data: {e}")
                continue
        
        return result