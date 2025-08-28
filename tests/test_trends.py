import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.trends.collector import RSSCollector

class TestRSSCollector(unittest.TestCase):

    @patch('src.trends.collector.feedparser')
    def test_collect_success(self, mock_feedparser):
        """
        Tests successful collection from multiple RSS feeds.
        """
        # Mock the return value of feedparser.parse
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

        feed_urls = ["http://feed1.com/rss", "http://feed2.com/rss"]
        collector = RSSCollector(feed_urls=feed_urls)
        results = collector.collect()

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'Test Title 1')
        self.assertEqual(results[1]['link'], 'http://test.com/2')
        self.assertEqual(mock_feedparser.parse.call_count, 2)

    @patch('src.trends.collector.feedparser')
    def test_collect_with_bozo_feed(self, mock_feedparser):
        """
        Tests collection with a malformed RSS feed.
        """
        mock_feed = MagicMock()
        mock_feed.bozo = 1
        mock_feed.bozo_exception = 'some error'
        mock_feed.entries = [
            MagicMock(title='Test Title 1', link='http://test.com/1', summary='Summary 1', published_parsed=(2023, 1, 1, 12, 0, 0, 0, 1, 0)),
        ]
        mock_feedparser.parse.return_value = mock_feed

        collector = RSSCollector(feed_urls=["http://malformed.com/rss"])
        results = collector.collect()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Test Title 1')

    @patch('src.trends.collector.feedparser')
    def test_collect_with_failed_feed(self, mock_feedparser):
        """
        Tests collection when a feed fails to parse.
        """
        mock_feedparser.parse.side_effect = Exception("Test exception")

        collector = RSSCollector(feed_urls=["http://failed.com/rss"])
        results = collector.collect()

        self.assertEqual(len(results), 0)

    def test_initialization_with_invalid_urls(self):
        """
        Tests that the collector raises a TypeError for invalid feed_urls type.
        """
        with self.assertRaises(TypeError):
            RSSCollector(feed_urls="not-a-list")

if __name__ == '__main__':
    unittest.main()

# We need to import the script we want to test
from scripts import collect_trends

class TestCollectTrendsScript(unittest.TestCase):

    @patch('scripts.collect_trends.RSSCollector')
    @patch('scripts.collect_trends.WebContentExtractor')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.dump')
    def test_main_script_flow(self, mock_json_dump, mock_open, MockWebContentExtractor, MockRSSCollector):
        """
        Tests the main flow of the collect_trends.py script.
        """
        # --- Setup Mocks ---
        # Mock RSSCollector to return a sample article
        mock_rss_collector = MockRSSCollector.return_value
        mock_rss_collector.collect.return_value = [{
            'title': 'Test Article',
            'link': 'http://example.com/article',
            'summary': 'A test summary.',
            'published_iso': '2023-01-01T12:00:00',
            'source_feed': 'http://example.com/feed'
        }]

        # Mock WebContentExtractor to return sample content
        mock_content_extractor = MockWebContentExtractor.return_value
        mock_content_extractor.extract_website_content.return_value = {
            'main_content': 'This is the full article content.',
            'headers': {'h1': ['Main Header']}
        }

        # --- Run the script's main function ---
        collect_trends.main()

        # --- Assertions ---
        # Assert that RSSCollector was initialized and called
        MockRSSCollector.assert_called_once_with(feed_urls=collect_trends.DESIGN_BLOG_FEEDS)
        mock_rss_collector.collect.assert_called_once()

        # Assert that WebContentExtractor was initialized and called
        MockWebContentExtractor.assert_called_once()
        mock_content_extractor.extract_website_content.assert_called_once_with('http://example.com/article')
        mock_content_extractor.close.assert_called_once()

        # Assert that the file was opened for writing
        self.assertTrue(any("data/trends/trends_" in str(call) for call in mock_open.call_args[0]))

        # Assert that json.dump was called with the correct data
        self.assertEqual(mock_json_dump.call_count, 1)
        written_data = mock_json_dump.call_args[0][0]
        self.assertEqual(len(written_data), 1)
        self.assertEqual(written_data[0]['title'], 'Test Article')
        self.assertEqual(written_data[0]['full_content'], 'This is the full article content.')
        self.assertIn('h1', written_data[0]['full_content_headers'])
