import unittest
from src.extractors.content_extractor import WebContentExtractor

class TestContentExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = WebContentExtractor()
    
    def test_extract_title(self):
        # Test cases here
        pass
    
    def tearDown(self):
        self.extractor.close()
