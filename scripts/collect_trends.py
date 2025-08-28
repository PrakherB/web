import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.trends.collector import RSSCollector

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

    collector = RSSCollector(feed_urls=DESIGN_BLOG_FEEDS)
    collected_articles = collector.collect()

    if not collected_articles:
        print("No articles collected. Exiting.")
        return

    # Save the collected data to a file
    output_dir = Path(__file__).parent.parent / "data" / "trends"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"trends_{timestamp}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(collected_articles, f, indent=2, ensure_ascii=False)

    print(f"✅ Successfully collected {len(collected_articles)} articles.")
    print(f"💾 Saved to: {output_file}")

if __name__ == "__main__":
    main()
