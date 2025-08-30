import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.reporting.generator import ReportPromptGenerator, get_sample_data_for_prompt

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

        # Check for competitor and trend formatting
        self.assertIn("1. Starbucks", prompt)
        self.assertIn("2. Blue Bottle Coffee", prompt)
        self.assertIn("1. Minimalism", prompt)
        self.assertIn("2. Sustainable Design", prompt)

    def test_generate_prompt_with_custom_template(self):
        """
        Tests prompt generation with a custom template.
        """
        custom_template = "Business: {BUSINESS_DESCRIPTION}, Industry: {INDUSTRY}"
        generator = ReportPromptGenerator(template=custom_template)
        sample_data = get_sample_data_for_prompt()
        prompt = generator.generate_prompt(**sample_data)

        expected_prompt = f"Business: {sample_data['business_description']}, Industry: {sample_data['industry_name']}"
        # The format method will not replace placeholders that are not in the template
        self.assertNotIn("NAICS_CODE", prompt)
        self.assertIn(sample_data['business_description'], prompt)

if __name__ == '__main__':
    unittest.main()
