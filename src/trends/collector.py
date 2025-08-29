import feedparser
import logging
import time
from datetime import datetime
import os
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RSSCollector:
    """
    Collects and parses trend data from RSS feeds.
    """
    def __init__(self, feed_urls):
        """
        Initializes the RSSCollector.

        :param feed_urls: A list of RSS feed URLs to parse.
        """
        if not isinstance(feed_urls, list):
            raise TypeError("feed_urls must be a list of strings.")
        self.feed_urls = feed_urls

    def _parse_published_date(self, entry):
        """
        Parses the published date from a feed entry and returns it in ISO 8601 format.
        """
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            return datetime.fromtimestamp(time.mktime(entry.published_parsed)).isoformat()
        if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            return datetime.fromtimestamp(time.mktime(entry.updated_parsed)).isoformat()
        return datetime.now().isoformat()

    def collect(self):
        """
        Fetches and parses the RSS feeds, returning a list of structured entries.
        """
        all_entries = []
        logging.info(f"Starting RSS feed collection for {len(self.feed_urls)} URLs.")

        for url in self.feed_urls:
            try:
                logging.info(f"Fetching feed: {url}")
                feed = feedparser.parse(url)

                if feed.bozo:
                    # The bozo bit is set to 1 if the feed is not well-formed
                    logging.warning(f"Feed at {url} is not well-formed. Bozo exception: {feed.bozo_exception}")

                for entry in feed.entries:
                    all_entries.append({
                        'title': getattr(entry, 'title', 'No Title'),
                        'link': getattr(entry, 'link', 'No Link'),
                        'summary': getattr(entry, 'summary', 'No Summary'),
                        'published_iso': self._parse_published_date(entry),
                        'source_feed': url
                    })
                logging.info(f"Successfully parsed {len(feed.entries)} entries from {url}")

            except Exception as e:
                logging.error(f"Failed to fetch or parse feed at {url}: {e}")

        logging.info(f"Finished RSS feed collection. Total entries collected: {len(all_entries)}")
        return all_entries

class DribbbleCollector:
    """
    Collects design trend data from the Dribbble API.
    """
    BASE_URL = "https://api.dribbble.com/v2/user/shots"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Dribbble API key is required.")
        self.api_key = api_key
        self.headers = {'Authorization': f'Bearer {self.api_key}'}

    def _transform_shot_to_article(self, shot: dict) -> dict:
        """
        Transforms a Dribbble shot object into the standard article format.
        """
        return {
            'title': shot.get('title', 'No Title'),
            'link': shot.get('html_url', 'No Link'),
            'summary': shot.get('description', 'No Summary'),
            'published_iso': shot.get('created_at', datetime.now().isoformat()),
            'source_feed': 'Dribbble API'
        }

    def collect(self, query: str = "web design trends", per_page: int = 20) -> list:
        """
        Fetches and transforms 'shots' from Dribbble based on a query.
        """
        params = {'q': query, 'per_page': per_page}
        transformed_shots = []
        try:
            response = requests.get(self.BASE_URL, headers=self.headers, params=params)
            response.raise_for_status()
            shots = response.json()
            for shot in shots:
                transformed_shots.append(self._transform_shot_to_article(shot))
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch data from Dribbble API: {e}")

        return transformed_shots
