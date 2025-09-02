import unittest
import json
from unittest.mock import patch, MagicMock

from src.api.routes import app
from src.reporting.models import CompetitorAnalysis, TrendIntegration # Import models for clarity

class TestIntegrationApi(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('src.api.routes.classifier') # Mock the classifier at the API level
    @patch('src.api.routes.extractor')
    @patch('src.api.routes.collect_and_process_trends')
    @patch('src.api.routes.find_similar_designs')
    def test_analyze_endpoint_integration(self, mock_find_similar, mock_collect_trends, mock_extractor, mock_classifier):
        # 1. Setup Mocks

        # Mock website content extraction
        mock_extractor.extract_website_content.return_value = {
            'main_content': 'This is a test website about innovative technology solutions and custom software development.',
            'title': 'Test Tech Inc.',
            'meta_description': 'Test Tech Inc. specializes in tech solutions.'
        }

        # Mock the classifier to return a predictable result
        mock_classifier.classify_business.return_value = {
            'predicted_naics_code': '541511',
            'predicted_industry': 'Custom Computer Programming Services',
            'confidence_score': 0.99
        }

        # Mock trend collection
        mock_collect_trends.return_value = [
            {
                'name': 'AI-driven Personalization',
                'relevance_score': 0.9,
                'summary': 'AI algorithms are being used to tailor user experiences in real-time.',
                'category': 'Technology',
                'source': 'dribbble'
            }
        ]

        # Mock vector search for competitors
        mock_competitors_data = [
            {
                "name": "Competitor A",
                "design_summary": "Minimalist design.",
                "competitor_url": "https://competitor-a.com",
                "screenshot_url": "https://example.com/screenshot_a.jpg",
                "design_pattern_analysis": "Grid layout.",
                "strengths": ["Clean UI"],
                "improvement_opportunities": ["Slow load time"]
            }
        ]
        mock_find_similar.return_value = {
            'metadatas': [mock_competitors_data]
        }

        # 2. Make API Request
        response = self.app.post('/api/v1/analyze',
                                 data=json.dumps({'url': 'http://example.com'}),
                                 content_type='application/json')

        # 3. Assertions
        self.assertEqual(response.status_code, 200, f"API call failed with status {response.status_code}: {response.text}")

        response_data = response.json

        # Now we can reliably check the output
        self.assertEqual(response_data['industry_analysis']['naics_code'], '541511')
        self.assertEqual(response_data['industry_analysis']['description'], 'Custom Computer Programming Services')

        self.assertEqual(len(response_data['competitor_design_analysis']), 1)
        self.assertEqual(response_data['competitor_design_analysis'][0]['name'], 'Competitor A')

        self.assertEqual(len(response_data['trend_integration']), 1)
        self.assertEqual(response_data['trend_integration'][0]['trend_name'], 'AI-driven Personalization')

        self.assertEqual(len(response_data['custom_recommendations']), 2)

if __name__ == '__main__':
    unittest.main()
