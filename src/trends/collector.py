import feedparser
import logging
import time
from datetime import datetime

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
