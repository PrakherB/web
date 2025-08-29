import re
import html
from datetime import datetime, timezone
import math

class TextProcessor:
    """
    Cleans and processes raw text content.
    """
    def clean_text(self, text: str) -> str:
        """
        Cleans HTML tags, decodes HTML entities, and removes extra whitespace from text.
        """
        if not text:
            return ""

        # Decode HTML entities
        text = html.unescape(text)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())

        return text

    def chunk_text(self, text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
        """
        Splits text into smaller, overlapping chunks.

        :param text: The text to be chunked.
        :param chunk_size: The number of words in each chunk.
        :param overlap: The number of words to overlap between chunks.
        :return: A list of text chunks.
        """
        if not isinstance(text, str) or not text.strip():
            return []

        if not isinstance(chunk_size, int) or not isinstance(overlap, int):
            raise TypeError("chunk_size and overlap must be integers.")

        if chunk_size <= overlap:
            raise ValueError("chunk_size must be greater than overlap.")

        words = text.split()
        chunks = []

        # Calculate the step size for the sliding window
        step = chunk_size - overlap

        for i in range(0, len(words), step):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():  # Only add non-empty chunks
                chunks.append(chunk)

        return chunks

    def calculate_recency_score(self, published_date_iso: str, decay_factor: float = 365) -> float:
        """
        Calculates a recency score for an article.

        :param published_date_iso: The publication date in ISO 8601 format.
        :param decay_factor: Controls how quickly the score decays. A smaller value means faster decay.
        :return: A score between 0 and 1.
        """
        try:
            # The fromisoformat method does not handle all timezone formats, so we handle Z manually
            if published_date_iso.endswith('Z'):
                published_date_iso = published_date_iso[:-1] + '+00:00'

            published_date = datetime.fromisoformat(published_date_iso)

            # Make sure the date is timezone-aware for correct comparison
            if published_date.tzinfo is None:
                published_date = published_date.replace(tzinfo=timezone.utc)

            current_date = datetime.now(timezone.utc)
            days_since_published = (current_date - published_date).days

            if days_since_published < 0:
                return 1.0  # For future-dated articles

            # Exponential decay formula
            score = math.exp(-days_since_published / decay_factor)
            return round(score, 4)

        except (ValueError, TypeError):
            # If date parsing fails, return a neutral score
            return 0.5
