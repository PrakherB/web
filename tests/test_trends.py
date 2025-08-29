import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.trends.collector import RSSCollector
from src.trends.processor import TextProcessor

class TestRSSCollector(unittest.TestCase):

    @patch('src.trends.collector.feedparser')
    def test_collect_success(self, mock_feedparser):
        # ... (existing test)
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

    def test_clean_text_empty(self):
        self.assertEqual(self.processor.clean_text(""), "")
        self.assertEqual(self.processor.clean_text(None), "")

    def test_chunk_text(self):
        text = "word " * 500
        chunks = self.processor.chunk_text(text, chunk_size=100, overlap=20)
        self.assertTrue(len(chunks) > 1)
        self.assertTrue(all(len(chunk.split()) <= 100 for chunk in chunks))

    def test_chunk_text_no_overlap(self):
        text = "word " * 200
        chunks = self.processor.chunk_text(text, chunk_size=50, overlap=0)
        self.assertEqual(len(chunks), 4)

    def test_chunk_text_errors(self):
        with self.assertRaises(ValueError):
            self.processor.chunk_text("some text", chunk_size=10, overlap=10)
        with self.assertRaises(TypeError):
            self.processor.chunk_text("some text", chunk_size="10", overlap=5)

# We need to import the script we want to test
from scripts import collect_trends

class TestCollectTrendsScript(unittest.TestCase):

    @patch('scripts.collect_trends.RSSCollector')
    @patch('scripts.collect_trends.WebContentExtractor')
    @patch('scripts.collect_trends.TextProcessor')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.dump')
    def test_main_script_flow(self, mock_json_dump, mock_open, MockTextProcessor, MockWebContentExtractor, MockRSSCollector):
        """
        Tests the main flow of the collect_trends.py script with text processing.
        """
        # --- Setup Mocks ---
        mock_rss_collector = MockRSSCollector.return_value
        mock_rss_collector.collect.return_value = [{'link': 'http://example.com/article'}]

        mock_content_extractor = MockWebContentExtractor.return_value
        mock_content_extractor.extract_website_content.return_value = {'main_content': 'full content'}

        mock_text_processor = MockTextProcessor.return_value
        mock_text_processor.clean_text.return_value = 'cleaned content'
        mock_text_processor.chunk_text.return_value = ['chunk1', 'chunk2']

        # --- Run the script's main function ---
        collect_trends.main()

        # --- Assertions ---
        MockRSSCollector.assert_called_once()
        MockWebContentExtractor.assert_called_once()
        MockTextProcessor.assert_called_once()

        mock_content_extractor.extract_website_content.assert_called_once_with('http://example.com/article')
        mock_text_processor.clean_text.assert_called_once_with('full content')
        mock_text_processor.chunk_text.assert_called_once_with('cleaned content')

        self.assertTrue(any("data/trends/trends_" in str(call) for call in mock_open.call_args[0]))

        written_data = mock_json_dump.call_args[0][0]
        self.assertEqual(len(written_data), 1)
        self.assertIn('content_chunks', written_data[0])
        self.assertEqual(written_data[0]['content_chunks'], ['chunk1', 'chunk2'])

if __name__ == '__main__':
    unittest.main()
