import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.trends.collector import RSSCollector
from src.extractors.content_extractor import WebContentExtractor

# A list of authoritative design trend RSS feeds
DESIGN_BLOG_FEEDS = [
    "https://www.smashingmagazine.com/feed/",
    "https://css-tricks.com/feed/",
    "https://www.awwwards.com/blog/feed/",
    "https://webdesignerdepot.com/feed/",
    "https://uxplanet.org/feed"
]

def main():
    """
    Runs the trend collection process and saves the results.
    """
    print("🚀 Starting trend data collection...")

    rss_collector = RSSCollector(feed_urls=DESIGN_BLOG_FEEDS)
    articles = rss_collector.collect()

    if not articles:
        print("No articles collected from RSS feeds. Exiting.")
        return

    print(f"📰 Collected {len(articles)} articles from RSS feeds. Now fetching full content...")

    content_extractor = WebContentExtractor()

    for article in articles:
        try:
            print(f"   -> Fetching content for: {article['link']}")
            content_data = content_extractor.extract_website_content(article['link'])
            if content_data:
                article['full_content'] = content_data.get('main_content', '')
                article['full_content_headers'] = content_data.get('headers', {})
            else:
                article['full_content'] = ''
                article['full_content_headers'] = {}
        except Exception as e:
            print(f"      ERROR fetching content for {article['link']}: {e}")
            article['full_content'] = ''
            article['full_content_headers'] = {}

    content_extractor.close()

    # Save the collected data to a file
    output_dir = Path(__file__).parent.parent / "data" / "trends"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"trends_{timestamp}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print(f"✅ Successfully processed {len(articles)} articles.")
    print(f"💾 Saved to: {output_file}")

if __name__ == "__main__":
    main()
