import sys
import json
from pathlib import Path
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.search.vector_search import EmbeddingManager, VectorDBManager

def load_naics_data():
    """Loads the comprehensive NAICS data from the JSON file."""
    naics_file = Path(__file__).parent.parent / "data" / "naics" / "comprehensive_naics_codes.json"
    if not naics_file.exists():
        print(f"Error: NAICS data file not found at {naics_file}")
        print("Please run 'scripts/build_comprehensive_naics_database.py' first.")
        sys.exit(1)

    with open(naics_file, 'r') as f:
        return json.load(f)

def main():
    """
    Builds the vector database from the analysis JSON files in data/outputs.
    """
    print("🚀 Starting vector database build...")

    embedding_manager = EmbeddingManager()
    vector_db_manager = VectorDBManager()

    print("Getting or creating ChromaDB collection...")
    collection = vector_db_manager.get_or_create_collection("design_inspirations")

    print("Loading NAICS data...")
    naics_data = load_naics_data()

    analysis_dir = Path(__file__).parent.parent / "data" / "outputs"
    analysis_files = list(analysis_dir.glob("*.json"))

    if not analysis_files:
        print(f"No analysis files found in {analysis_dir}")
        return

    documents = []
    embeddings = []
    metadatas = []
    ids = []

    print(f"Processing {len(analysis_files)} analysis files...")
    for i, file_path in enumerate(analysis_files):
        with open(file_path, 'r') as f:
            data = json.load(f)

        company_name = data.get('url').split('//')[-1].split('/')[0]
        description = data.get('meta_description', '')
        if not description or description == "None":
            description = data.get('title', '')

        industry_keywords = data.get('key_business_phrases', [])
        primary_naics = data.get('classification', {}).get('naics_code')

        naics_info = naics_data.get(primary_naics, {})
        naics_description = naics_info.get('description', '')

        composite_text = (
            f"Company: {company_name}. "
            f"Description: {description}. "
            f"Industry Keywords: {', '.join(industry_keywords)}. "
            f"NAICS Description: {naics_description}"
        )

        embedding = embedding_manager.generate_embedding(composite_text)

        documents.append(composite_text)
        embeddings.append(embedding.tolist())
        metadatas.append({
            "company_name": company_name,
            "domain": data.get('url'),
            "primary_naics": primary_naics
        })
        # Use index as ID since we don't have a database ID
        ids.append(str(i))

    print(f"Adding {len(documents)} documents to the vector database...")
    if documents:
        vector_db_manager.add_documents(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    print("✅ Vector database build complete!")

if __name__ == "__main__":
    main()
