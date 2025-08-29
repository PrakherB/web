import re
import html

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
