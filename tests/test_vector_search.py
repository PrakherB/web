import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import sys
sys.path.insert(0, '.')

from src.search.vector_search import EmbeddingManager, VectorDBManager, find_similar_designs

class TestVectorSearch(unittest.TestCase):

    @patch('src.search.vector_search.SentenceTransformer')
    def test_embedding_manager(self, MockSentenceTransformer):
        """
        Tests the EmbeddingManager class.
        """
        mock_model = MockSentenceTransformer.return_value
        mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])

        manager = EmbeddingManager()
        embedding = manager.generate_embedding("test text")

        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape, (3,))
        mock_model.encode.assert_called_with("test text")

    @patch('src.search.vector_search.chromadb')
    def test_vector_db_manager(self, mock_chromadb):
        """
        Tests the VectorDBManager class.
        """
        mock_collection = MagicMock()
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.PersistentClient.return_value = mock_client

        manager = VectorDBManager()
        collection = manager.get_or_create_collection("test_collection")

        self.assertIsNotNone(collection)
        mock_client.get_or_create_collection.assert_called_with(name="test_collection")

        manager.add_documents(
            documents=["doc1"],
            embeddings=[[0.1, 0.2, 0.3]],
            metadatas=[{"meta": "data"}],
            ids=["1"]
        )
        mock_collection.add.assert_called_with(
            embeddings=[[0.1, 0.2, 0.3]],
            documents=["doc1"],
            metadatas=[{"meta": "data"}],
            ids=["1"]
        )

        manager.query(query_embedding=[0.4, 0.5, 0.6], n_results=5)
        mock_collection.query.assert_called_with(
            query_embeddings=[[0.4, 0.5, 0.6]],
            n_results=5,
            where=None
        )

    @patch('src.search.vector_search.EmbeddingManager')
    @patch('src.search.vector_search.VectorDBManager')
    def test_find_similar_designs(self, MockVectorDBManager, MockEmbeddingManager):
        """
        Tests the find_similar_designs function.
        """
        # Setup mocks
        mock_embedding_manager = MockEmbeddingManager.return_value
        mock_embedding_manager.generate_embedding.return_value = np.array([0.1, 0.2, 0.3])

        mock_db_manager = MockVectorDBManager.return_value
        mock_db_manager.query.return_value = {"ids": [["1", "2"]]}

        # Test without NAICS filter
        results = find_similar_designs("test description")

        mock_embedding_manager.generate_embedding.assert_called_with("test description")
        mock_db_manager.get_or_create_collection.assert_called_with("design_inspirations")
        mock_db_manager.query.assert_called_with(
            query_embedding=[0.1, 0.2, 0.3],
            n_results=10,
            where=None
        )
        self.assertEqual(results, {"ids": [["1", "2"]]})

        # Test with NAICS filter
        results = find_similar_designs("test description", naics_category="123456")

        mock_db_manager.query.assert_called_with(
            query_embedding=[0.1, 0.2, 0.3],
            n_results=10,
            where={"primary_naics": "123456"}
        )

if __name__ == '__main__':
    unittest.main()
