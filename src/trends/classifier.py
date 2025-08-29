from transformers import pipeline
import json
from pathlib import Path

class TrendClassifier:
    """
    Classifies text chunks into predefined trend categories.
    """
    def __init__(self):
        # This will be initialized with a zero-shot classification model
        self.classifier = None
        self.trend_categories = [
            "Visual Design",
            "Layout & Structure",
            "Interaction Design",
            "Technology Trends",
            "Industry-Specific Patterns"
        ]

    def load_model(self, model_name="facebook/bart-large-mnli"):
        """
        Loads the zero-shot classification model.
        """
        self.classifier = pipeline("zero-shot-classification", model=model_name)

    def classify_chunk(self, chunk: str, threshold=0.7) -> list[str]:
        """
        Classifies a single text chunk.
        """
        if not self.classifier:
            self.load_model()

        results = self.classifier(chunk, self.trend_categories, multi_label=True)

        # Filter results by a confidence threshold
        top_categories = []
        for i, score in enumerate(results['scores']):
            if score > threshold:
                top_categories.append(results['labels'][i])

        return top_categories

    def _load_industries(self):
        """
        Loads industry titles from the NAICS data file.
        """
        naics_file = Path(__file__).parent.parent.parent / "data" / "naics" / "comprehensive_naics_codes.json"
        if not hasattr(self, '_industry_list') or not self._industry_list:
            with open(naics_file, 'r') as f:
                naics_data = json.load(f)
            # We only want the titles for classification
            self._industry_list = [details['title'] for details in naics_data.values()]
        return self._industry_list

    def classify_industries(self, text: str, threshold=0.6, top_n=3) -> list[str]:
        """
        Classifies text against a list of industries.
        """
        if not self.classifier:
            self.load_model()

        industries = self._load_industries()

        results = self.classifier(text, industries, multi_label=True)

        # Get the top N industries above the threshold
        relevant_industries = []
        for i, score in enumerate(results['scores']):
            if score > threshold:
                relevant_industries.append(results['labels'][i])

        return relevant_industries[:top_n]
