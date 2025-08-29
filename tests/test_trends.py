import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.trends.collector import RSSCollector
from src.trends.processor import TextProcessor
from src.trends.classifier import TrendClassifier

class TestRSSCollector(unittest.TestCase):

    @patch('src.trends.collector.feedparser')
    def test_collect_success(self, mock_feedparser):
        """
        Tests successful collection from multiple RSS feeds.
        """
        mock_feed1 = MagicMock()
        mock_feed1.bozo = 0
        mock_feed1.entries = [
            MagicMock(title='Test Title 1', link='http://test.com/1', summary='Summary 1', published_parsed=(2023, 1, 1, 12, 0, 0, 0, 1, 0)),
        ]
        mock_feed2 = MagicMock()
        mock_feed2.bozo = 0
        mock_feed2.entries = [
            MagicMock(title='Test Title 2', link='http://test.com/2', summary='Summary 2', published_parsed=(2023, 1, 2, 12, 0, 0, 0, 2, 0)),
        ]
        mock_feedparser.parse.side_effect = [mock_feed1, mock_feed2]
        collector = RSSCollector(feed_urls=["http://feed1.com/rss", "http://feed2.com/rss"])
        results = collector.collect()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'Test Title 1')

class TestTextProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = TextProcessor()

    def test_clean_text(self):
        raw_html = "<p>This is a &lt;b&gt;bold&lt;/b&gt; statement.&nbsp;</p>"
        cleaned_text = "This is a bold statement."
        self.assertEqual(self.processor.clean_text(raw_html), cleaned_text)

    def test_chunk_text(self):
        text = "word " * 500
        chunks = self.processor.chunk_text(text, chunk_size=100, overlap=20)
        self.assertTrue(len(chunks) > 1)
        self.assertTrue(all(len(chunk.split()) <= 100 for chunk in chunks))

class TestTrendClassifier(unittest.TestCase):

    @patch('src.trends.classifier.pipeline')
    def test_classify_chunk(self, mock_pipeline):
        """
        Tests the classify_chunk method.
        """
        mock_classifier = MagicMock()
        mock_classifier.return_value = {
            'labels': ['Visual Design', 'Technology Trends'],
            'scores': [0.9, 0.6]
        }
        mock_pipeline.return_value = mock_classifier

        classifier = TrendClassifier()
        categories = classifier.classify_chunk("some text about design", threshold=0.8)

        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0], 'Visual Design')

# We need to import the script we want to test
from scripts import collect_trends

class TestCollectTrendsScript(unittest.TestCase):

    @patch('scripts.collect_trends.RSSCollector')
    @patch('scripts.collect_trends.WebContentExtractor')
    @patch('scripts.collect_trends.TextProcessor')
    @patch('scripts.collect_trends.TrendClassifier')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.dump')
    def test_main_script_flow(self, mock_json_dump, mock_open, MockTrendClassifier, MockTextProcessor, MockWebContentExtractor, MockRSSCollector):
        """
        Tests the main flow of the collect_trends.py script with classification.
        """
        # --- Setup Mocks ---
        mock_rss_collector = MockRSSCollector.return_value
        mock_rss_collector.collect.return_value = [{'link': 'http://example.com/article'}]

        mock_content_extractor = MockWebContentExtractor.return_value
        mock_content_extractor.extract_website_content.return_value = {'main_content': 'full content'}

        mock_text_processor = MockTextProcessor.return_value
        mock_text_processor.chunk_text.return_value = ['chunk1']

        mock_trend_classifier = MockTrendClassifier.return_value
        mock_trend_classifier.classify_chunk.return_value = ['Visual Design']

        # --- Run the script's main function ---
        collect_trends.main()

        # --- Assertions ---
        mock_trend_classifier.classify_chunk.assert_called_once_with('chunk1')

        written_data = mock_json_dump.call_args[0][0]
        self.assertIn('classified_chunks', written_data[0])
        self.assertEqual(len(written_data[0]['classified_chunks']), 1)
        self.assertEqual(written_data[0]['classified_chunks'][0]['categories'], ['Visual Design'])

if __name__ == '__main__':
    unittest.main()
