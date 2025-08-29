from transformers import pipeline

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
