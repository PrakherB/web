import chromadb
from sentence_transformers import SentenceTransformer

class EmbeddingManager:
    """
    Manages the creation of text embeddings.
    """
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initializes the EmbeddingManager with a sentence transformer model.

        :param model_name: The name of the sentence transformer model to use.
        """
        self.model = SentenceTransformer(model_name)

    def generate_embedding(self, text):
        """
        Generates an embedding for the given text.

        :param text: The text to embed.
        :return: A numpy array representing the embedding.
        """
        return self.model.encode(text)

class VectorDBManager:
    """
    Manages the vector database (ChromaDB).
    """
    def __init__(self, path="./chroma_db"):
        """
        Initializes the VectorDBManager and connects to the database.

        :param path: The path to the ChromaDB database directory.
        """
        self.client = chromadb.PersistentClient(path=path)
        self.collection = None

    def get_or_create_collection(self, name="design_inspirations"):
        """
        Gets or creates a collection in ChromaDB.

        :param name: The name of the collection.
        :return: The ChromaDB collection object.
        """
        self.collection = self.client.get_or_create_collection(name=name)
        return self.collection

    def add_documents(self, documents, embeddings, metadatas, ids):
        """
        Adds documents and their embeddings to the collection.

        :param documents: A list of documents (text).
        :param embeddings: A list of embeddings.
        :param metadatas: A list of metadata dictionaries.
        :param ids: A list of unique IDs for the documents.
        """
        if self.collection is None:
            raise Exception("Collection not initialized. Call get_or_create_collection() first.")

        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_embedding, n_results=10, where=None):
        """
        Queries the collection for similar documents.

        :param query_embedding: The embedding of the query text.
        :param n_results: The number of results to return.
        :param where: A dictionary for filtering results.
        :return: A list of similar documents.
        """
        if self.collection is None:
            raise Exception("Collection not initialized. Call get_or_create_collection() first.")

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )

def find_similar_designs(business_description, naics_category=None, top_k=10):
    """
    Finds similar designs based on a business description and optional NAICS category.

    :param business_description: The description of the business to find designs for.
    :param naics_category: (Optional) The NAICS category to filter by.
    :param top_k: The number of similar designs to return.
    :return: A list of similar designs.
    """
    embedding_manager = EmbeddingManager()
    vector_db_manager = VectorDBManager()

    vector_db_manager.get_or_create_collection("design_inspirations")

    query_embedding = embedding_manager.generate_embedding(business_description).tolist()

    where_filter = {}
    if naics_category:
        where_filter = {"primary_naics": naics_category}

    results = vector_db_manager.query(
        query_embedding=query_embedding,
        n_results=top_k,
        where=where_filter if where_filter else None
    )

    return results
