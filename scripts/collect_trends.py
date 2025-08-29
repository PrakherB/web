import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.trends.collector import RSSCollector
from src.extractors.content_extractor import WebContentExtractor
from src.trends.processor import TextProcessor

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

    print(f"📰 Collected {len(articles)} articles from RSS feeds. Now fetching and processing full content...")

    content_extractor = WebContentExtractor()
    text_processor = TextProcessor()

    for article in articles:
        try:
            print(f"   -> Processing: {article['link']}")
            content_data = content_extractor.extract_website_content(article['link'])

            if content_data and content_data.get('main_content'):
                full_content = content_data['main_content']
                cleaned_content = text_processor.clean_text(full_content)
                content_chunks = text_processor.chunk_text(cleaned_content)
                article['content_chunks'] = content_chunks
            else:
                article['content_chunks'] = []

        except Exception as e:
            print(f"      ERROR processing article {article['link']}: {e}")
            article['content_chunks'] = []

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
