import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.reporting.generator import ReportPromptGenerator, ReportBuilder, get_sample_data_for_prompt
from src.reporting.models import DesignReport

class TestReportPromptGenerator(unittest.TestCase):

    def test_generate_prompt_with_sample_data(self):
        """
        Tests the prompt generation with sample data.
        """
        generator = ReportPromptGenerator()
        sample_data = get_sample_data_for_prompt()
        prompt = generator.generate_prompt(**sample_data)

        # Check that all the data is in the prompt
        self.assertIn(sample_data['industry_name'], prompt)
        self.assertIn(sample_data['business_description'], prompt)
        self.assertIn(sample_data['naics_code'], prompt)

class TestReportBuilder(unittest.TestCase):

    def test_build_report(self):
        """
        Tests the report building process.
        """
        builder = ReportBuilder()
        sample_data = get_sample_data_for_prompt()
        report = builder.build(sample_data)

        self.assertIsInstance(report, DesignReport)
        self.assertEqual(report.industry_analysis.naics_code, sample_data['naics_code'])
        self.assertEqual(len(report.competitor_design_analysis), 2)
        self.assertEqual(report.competitor_design_analysis[0].name, "Starbucks")
        self.assertEqual(len(report.trend_integration), 3)
        self.assertEqual(report.trend_integration[0].trend_name, "Minimalism")

if __name__ == '__main__':
    unittest.main()
