"""
Direct Test - Add One Document to Vector Store
This will help us see exactly what's happening
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DBManager
from processors.document_processor import DocumentProcessor
from processors.text_chunker import TextChunker
from processors.vector_store_manager import VectorStoreManager
from dotenv import load_dotenv

load_dotenv()

def test_add_document(user_id: int):
    """Test adding a single document"""
    
    print("=" * 70)
    print("DIRECT TEST - Add One Document")
    print("=" * 70)
    
    db = DBManager()
    
    # Get the first processed document
    documents = db.get_user_documents(user_id)
    if not documents:
        print("No documents found!")
        return
    
    # Use the first document
    doc = documents[0]
    print(f"\n1. Testing with document: {doc.file_name} (ID: {doc.id})")
    print(f"   File path: {doc.file_path}")
    print(f"   Exists: {os.path.exists(doc.file_path)}")
    
    # Process document
    print("\n2. Processing document...")
    processor = DocumentProcessor()
    processed = processor.process_document(doc.file_path)
    
    if not processed.get('success'):
        print(f"   ✗ Failed: {processed.get('error')}")
        return
    
    print(f"   ✓ Document processed")
    print(f"   Full text length: {len(processed.get('full_text', ''))}")
    
    # Chunk it
    print("\n3. Chunking document...")
    chunker = TextChunker()
    chunk_metadata = {
        'user_id': user_id,
        'document_id': doc.id,
        'document_type': doc.document_type,
        'file_name': doc.file_name
    }
    
    chunks = chunker.chunk_document(processed, chunk_metadata)
    print(f"   ✓ Created {len(chunks)} chunks")
    
    if chunks:
        print(f"   Sample chunk:")
        print(f"   - Text length: {len(chunks[0]['text'])}")
        print(f"   - First 100 chars: {chunks[0]['text'][:100]}...")
    
    # Initialize vector store
    print("\n4. Initializing vector store...")
    vector_store = VectorStoreManager()
    
    # Add chunks
    print("\n5. Adding chunks to vector store...")
    print("   This is where it might fail. Watch for errors...")
    
    try:
        success = vector_store.add_chunks(user_id, chunks, chunk_metadata)
        
        if success:
            print(f"   ✓ add_chunks returned True")
        else:
            print(f"   ✗ add_chunks returned False")
            
    except Exception as e:
        print(f"   ✗ Exception during add_chunks: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Verify
    print("\n6. Verifying...")
    try:
        stats = vector_store.get_collection_stats(user_id)
        chunk_count = stats.get('total_chunks', 0)
        
        print(f"   Vector store chunks: {chunk_count}")
        
        if chunk_count > 0:
            print(f"\n   🎉 SUCCESS! {chunk_count} chunks are in the vector store!")
            
            # Try a search
            print("\n7. Testing search...")
            results = vector_store.search_similar(user_id, "credit card", k=3)
            print(f"   Found {len(results)} results for 'credit card'")
            
            if results:
                print(f"   Sample result:")
                print(f"   {results[0]['content'][:150]}...")
        else:
            print(f"\n   ✗ FAILED: No chunks in vector store despite add_chunks returning {success}")
            
    except Exception as e:
        print(f"   ✗ Error verifying: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("AI Financial Coach - Direct Test")
    print("=" * 70)
    
    user_id = 1  # Default to user 1
    
    try:
        test_add_document(user_id)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
