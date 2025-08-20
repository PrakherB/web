import requests
from typing import Optional, Dict
from bs4 import BeautifulSoup
from .content_extractor import WebContentExtractor  # Fixed import

class ScrapingAPIBackup:
    """Backup scraping service using commercial APIs"""
    
    def __init__(self, api_key: str, service: str = "scrapingbee"):
        self.api_key = api_key
        self.service = service
        self.base_urls = {
            "scrapingbee": "https://app.scrapingbee.com/api/v1",
            "apify": "https://api.apify.com/v2"
        }
    
    def extract_with_api(self, url: str) -> Optional[Dict]:
        """Extract content using commercial API as backup"""
        try:
            if self.service == "scrapingbee":
                return self._scrapingbee_extract(url)
            elif self.service == "apify":
                return self._apify_extract(url)
        except Exception as e:
            print(f"API extraction failed: {e}")
            return None
    
    def _scrapingbee_extract(self, url: str) -> Dict:
        """Use ScrapingBee API"""
        params = {
            'api_key': self.api_key,
            'url': url,
            'render_js': 'true',
            'premium_proxy': 'true'
        }
        
        response = requests.get(self.base_urls["scrapingbee"], params=params)
        response.raise_for_status()
        
        # Process the HTML response similar to BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Create a temporary extractor instance to use its methods
        temp_extractor = WebContentExtractor()
        result = {
            'title': temp_extractor.extract_title(soup),
            'meta_description': temp_extractor.extract_meta_description(soup),
            'headers': temp_extractor.extract_headers(soup),
            'navigation': temp_extractor.extract_navigation(soup),
            'main_content': temp_extractor.extract_main_content(soup),
            'about_content': temp_extractor.extract_about_content(soup),
            'services_content': temp_extractor.extract_services_content(soup),
            'footer_content': temp_extractor.extract_footer_content(soup),
            'key_phrases': temp_extractor.extract_key_phrases(soup)
        }
        
        # Cleanup temp extractor
        temp_extractor.close()
        return result
    
    def _apify_extract(self, url: str) -> Dict:
        """Use Apify API"""
        # Placeholder for Apify implementation
        return {"error": "Apify implementation not yet available"}
