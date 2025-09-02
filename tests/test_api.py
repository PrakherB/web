import unittest
import json
from unittest.mock import patch

from src.api.routes import app

class TestApi(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('src.api.routes.extractor')
    @patch('src.api.routes.classifier')
    @patch('src.api.routes.find_similar_designs')
    @patch('src.api.routes.collect_and_process_trends')
    @patch('src.api.routes.ReportBuilder')
    def test_analyze_endpoint(self, MockReportBuilder, mock_collect_trends, mock_find_similar, mock_classifier, mock_extractor):
        # Setup mocks
        mock_extractor.extract_website_content.return_value = {'main_content': 'some content'}
        mock_classifier.classify_business.return_value = {'predicted_naics_code': '123456', 'predicted_industry': 'Test Industry'}
        mock_find_similar.return_value = {'metadatas': [[]]}
        mock_collect_trends.return_value = []

        mock_report_builder = MockReportBuilder.return_value
        mock_report_builder.build.return_value.model_dump.return_value = {"report": "test"}

        # Make request
        response = self.app.post('/api/v1/analyze',
                                 data=json.dumps({'url': 'http://example.com'}),
                                 content_type='application/json')

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"report": "test"})
        mock_extractor.extract_website_content.assert_called_once_with('http://example.com')
        mock_classifier.classify_business.assert_called_once()
        mock_find_similar.assert_called_once()
        mock_collect_trends.assert_called_once()
        mock_report_builder.build.assert_called_once()

if __name__ == '__main__':
    unittest.main()
