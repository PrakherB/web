import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.trends.collector import RSSCollector
from src.extractors.content_extractor import WebContentExtractor
from src.trends.processor import TextProcessor
from src.trends.classifier import TrendClassifier

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

    print(f"📰 Collected {len(articles)} articles from RSS feeds. Now fetching, processing, and classifying content...")

    content_extractor = WebContentExtractor()
    text_processor = TextProcessor()
    trend_classifier = TrendClassifier()

    for article in articles:
        try:
            print(f"   -> Processing: {article['link']}")
            content_data = content_extractor.extract_website_content(article['link'])

            if content_data and content_data.get('main_content'):
                full_content = content_data['main_content']
                cleaned_content = text_processor.clean_text(full_content)
                content_chunks = text_processor.chunk_text(cleaned_content)

                # Classify chunks
                classified_chunks = []
                for chunk in content_chunks:
                    categories = trend_classifier.classify_chunk(chunk)
                    if categories:
                        classified_chunks.append({
                            "chunk_text": chunk,
                            "categories": categories
                        })
                article['classified_chunks'] = classified_chunks

                # Calculate recency score
                article['recency_score'] = text_processor.calculate_recency_score(article['published_iso'])

                # Map to industries
                article['relevant_industries'] = trend_classifier.classify_industries(cleaned_content)

            else:
                article['classified_chunks'] = []
                article['recency_score'] = 0.0
                article['relevant_industries'] = []

        except Exception as e:
            print(f"      ERROR processing article {article['link']}: {e}")
            article['classified_chunks'] = []
            article['recency_score'] = 0.0
            article['relevant_industries'] = []

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
