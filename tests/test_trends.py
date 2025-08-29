import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.trends.collector import RSSCollector, DribbbleCollector
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

class TestDribbbleCollector(unittest.TestCase):

    @patch('src.trends.collector.requests.get')
    def test_collect_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [{
            'title': 'Dribbble Shot',
            'html_url': 'http://dribbble.com/shot',
            'description': 'A Dribbble shot description.',
            'created_at': '2023-01-01T12:00:00Z'
        }]
        mock_get.return_value = mock_response

        collector = DribbbleCollector(api_key="test_key")
        results = collector.collect()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Dribbble Shot')
        self.assertEqual(results[0]['source_feed'], 'Dribbble API')

class TestTextProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = TextProcessor()

    def test_calculate_recency_score(self):
        # Test with a recent date
        recent_date = datetime.now().isoformat()
        self.assertAlmostEqual(self.processor.calculate_recency_score(recent_date), 1.0, places=2)

        # Test with a date from a year ago
        one_year_ago = (datetime.now() - timedelta(days=365)).isoformat()
        self.assertAlmostEqual(self.processor.calculate_recency_score(one_year_ago), 0.37, places=2)

class TestTrendClassifier(unittest.TestCase):

    @patch('src.trends.classifier.pipeline')
    @patch('src.trends.classifier.json.load')
    @patch('builtins.open')
    def test_classify_industries(self, mock_open, mock_json_load, mock_pipeline):
        """
        Tests the classify_industries method.
        """
        mock_classifier = MagicMock()
        mock_classifier.return_value = {
            'labels': ['Finance and Insurance', 'Retail Trade'],
            'scores': [0.9, 0.5]
        }
        mock_pipeline.return_value = mock_classifier
        mock_json_load.return_value = {"52": {"title": "Finance and Insurance"}, "44": {"title": "Retail Trade"}}

        classifier = TrendClassifier()
        industries = classifier.classify_industries("some text about finance", threshold=0.8)

        self.assertEqual(len(industries), 1)
        self.assertEqual(industries[0], 'Finance and Insurance')

# We need to import the script we want to test
from scripts import collect_trends

class TestCollectTrendsScript(unittest.TestCase):

    @patch('scripts.collect_trends.RSSCollector')
    @patch('scripts.collect_trends.WebContentExtractor')
    @patch('scripts.collect_trends.TextProcessor')
    @patch('scripts.collect_trends.TrendClassifier')
    @patch('os.getenv')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.dump')
    def test_main_script_flow(self, mock_json_dump, mock_open, mock_getenv, MockTrendClassifier, MockTextProcessor, MockWebContentExtractor, MockRSSCollector):
        """
        Tests the main flow of the collect_trends.py script with all processing steps.
        """
        # --- Setup Mocks ---
        mock_getenv.return_value = "fake_dribbble_key"
        mock_rss_collector = MockRSSCollector.return_value
        mock_rss_collector.collect.return_value = [{'link': 'http://example.com/article', 'published_iso': datetime.now().isoformat()}]

        mock_content_extractor = MockWebContentExtractor.return_value
        mock_content_extractor.extract_website_content.return_value = {'main_content': 'full content'}

        mock_text_processor = MockTextProcessor.return_value
        mock_text_processor.chunk_text.return_value = ['chunk1']
        mock_text_processor.calculate_recency_score.return_value = 0.99

        mock_trend_classifier = MockTrendClassifier.return_value
        mock_trend_classifier.classify_chunk.return_value = ['Visual Design']
        mock_trend_classifier.classify_industries.return_value = ['Technology']

        # --- Run the script's main function ---
        collect_trends.main()

        # --- Assertions ---
        mock_trend_classifier.classify_industries.assert_called_once()
        mock_text_processor.calculate_recency_score.assert_called_once()

        written_data = mock_json_dump.call_args[0][0]
        self.assertIn('recency_score', written_data[0])
        self.assertEqual(written_data[0]['recency_score'], 0.99)
        self.assertIn('relevant_industries', written_data[0])
        self.assertEqual(written_data[0]['relevant_industries'], ['Technology'])

if __name__ == '__main__':
    unittest.main()
