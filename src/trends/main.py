import os
import json
from pathlib import Path
from datetime import datetime

from .collector import RSSCollector, DribbbleCollector
from .processor import TextProcessor
from .classifier import TrendClassifier
from src.extractors.content_extractor import WebContentExtractor

def collect_and_process_trends(feed_urls, dribbble_api_key=None):
    """
    Collects and processes trends from RSS feeds and Dribbble.
    """
    # --- RSS Collection ---
    rss_collector = RSSCollector(feed_urls=feed_urls)
    articles = rss_collector.collect()

    # --- Dribbble Collection ---
    if dribbble_api_key:
        dribbble_collector = DribbbleCollector(api_key=dribbble_api_key)
        dribbble_articles = dribbble_collector.collect()
        articles.extend(dribbble_articles)

    if not articles:
        return []

    # --- Processing and Classification ---
    content_extractor = WebContentExtractor()
    text_processor = TextProcessor()
    trend_classifier = TrendClassifier()

    for article in articles:
        try:
            content_data = content_extractor.extract_website_content(article['link'])

            if content_data and content_data.get('main_content'):
                full_content = content_data['main_content']
                cleaned_content = text_processor.clean_text(full_content)
                article['content_chunks'] = text_processor.chunk_text(cleaned_content)
                article['recency_score'] = text_processor.calculate_recency_score(article['published_iso'])
                article['relevant_industries'] = trend_classifier.classify_industries(cleaned_content)
            else:
                article['content_chunks'] = []
                article['recency_score'] = 0.0
                article['relevant_industries'] = []

        except Exception as e:
            article['content_chunks'] = []
            article['recency_score'] = 0.0
            article['relevant_industries'] = []

    content_extractor.close()
    return articles
