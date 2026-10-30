"""
Batch Process Script - Process all documents in data/processed folder
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.core.rag_engine import rag_engine
from backend.services.vector_service import vector_service


def main():
    """Process all documents in data/processed directory"""
    
    print("=" * 60)
    print("AI RAG Waterproofing Chatbot - Batch Data Processing")
    print("=" * 60)
    
    # Get the data/processed directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    processed_dir = os.path.join(project_root, "data", "processed")
    
    if not os.path.exists(processed_dir):
        print(f"Error: Directory not found: {processed_dir}")
        print("Please create the data/processed directory and add your documents.")
        return
    
    print(f"\nProcessing directory: {processed_dir}")
    print("Vector DB: ChromaDB persistent storage")
    
    # Get current stats
    stats = vector_service.get_collection_stats()
    print(f"\nCurrent document count in vector store: {stats.get('document_count', 0)}")
    
    # Ask for confirmation
    response = input("\nDo you want to process all documents in data/processed? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return
    
    print("\nProcessing documents...")
    print("-" * 60)
    
    # Process the directory
    result = rag_engine.ingest_directory(
        directory_path=processed_dir,
        metadata={"source": "data/processed"}
    )
    
    # Print results
    print("\n" + "=" * 60)
    print("Processing Complete!")
    print("=" * 60)
    print(f"Total files found: {result['total_files']}")
    print(f"Successfully processed: {result['successful']}")
    print(f"Failed: {result['failed']}")
    
    if result['errors']:
        print("\nErrors:")
        for error in result['errors']:
            print(f"  - {error['file']}: {error['error']}")
    
    # Get new stats
    new_stats = vector_service.get_collection_stats()
    print(f"\nNew document count in vector store: {new_stats.get('document_count', 0)}")
    print(f"Documents added: {new_stats.get('document_count', 0) - stats.get('document_count', 0)}")
    
    print("\nDone! Your documents are now ready for RAG queries.")


if __name__ == "__main__":
    main()
