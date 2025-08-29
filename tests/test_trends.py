import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.trends.collector import RSSCollector
from src.trends.processor import TextProcessor
from src.trends.classifier import TrendClassifier

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
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.dump')
    def test_main_script_flow(self, mock_json_dump, mock_open, MockTrendClassifier, MockTextProcessor, MockWebContentExtractor, MockRSSCollector):
        """
        Tests the main flow of the collect_trends.py script with all processing steps.
        """
        # --- Setup Mocks ---
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
