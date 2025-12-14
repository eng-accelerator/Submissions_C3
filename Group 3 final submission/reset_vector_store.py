"""
Complete Reset and Rebuild Vector Store
This will clear all embeddings and reprocess all documents from scratch
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DBManager
from processors.rag_system import RAGSystem
from dotenv import load_dotenv
import shutil

load_dotenv()

def reset_and_rebuild(user_id: int):
    """Reset vector store and rebuild from documents"""
    
    print("=" * 70)
    print("RESET AND REBUILD VECTOR STORE")
    print("=" * 70)
    
    db = DBManager()
    rag = RAGSystem(db_manager=db)
    
    # Step 1: Get documents
    print("\n1. Checking documents...")
    documents = db.get_user_documents(user_id)
    print(f"   Found {len(documents)} documents")
    
    if len(documents) == 0:
        print("   No documents to process!")
        return
    
    # Step 2: Clear vector store
    print("\n2. Clearing vector store...")
    print("   This will delete all existing embeddings.")
    
    response = input("   Continue? (y/n): ")
    if response.lower() != 'y':
        print("   Cancelled.")
        return
    
    try:
        success = rag.vector_store.clear_user_collection(user_id)
        if success:
            print("   ✓ Vector store cleared")
        else:
            print("   Note: Vector store may have been empty")
    except Exception as e:
        print(f"   Note: {e}")
    
    # Step 3: Rebuild embeddings
    print(f"\n3. Rebuilding embeddings for {len(documents)} documents...")
    print("   This may take a few minutes...\n")
    
    success_count = 0
    fail_count = 0
    total_chunks = 0
    
    for i, doc in enumerate(documents, 1):
        print(f"   [{i}/{len(documents)}] Processing {doc.file_name}...")
        
        try:
            result = rag.process_uploaded_document(
                user_id=user_id,
                file_path=doc.file_path,
                document_type=doc.document_type,
                file_name=doc.file_name
            )
            
            if result['success']:
                chunks = result.get('chunks_created', 0)
                vectors = result.get('vectors_created', 0)
                print(f"      ✓ Success: {chunks} chunks, {vectors} embeddings")
                success_count += 1
                total_chunks += chunks
            else:
                print(f"      ✗ Failed: {result['message']}")
                fail_count += 1
                
        except Exception as e:
            print(f"      ✗ Error: {e}")
            fail_count += 1
    
    # Step 4: Verify
    print(f"\n4. Verification...")
    try:
        stats = rag.vector_store.get_collection_stats(user_id)
        print(f"   Vector store now has {stats['total_chunks']} chunks")
        print(f"   Successfully processed: {success_count} documents")
        print(f"   Failed: {fail_count} documents")
        print(f"   Total chunks created: {total_chunks}")
    except Exception as e:
        print(f"   Could not verify: {e}")
    
    print("\n" + "=" * 70)
    print("REBUILD COMPLETE!")
    print("=" * 70)
    print("\nYou can now use the Chat page to search your documents.")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("AI Financial Coach - Vector Store Reset Tool")
    print("=" * 70)
    
    # Get user ID
    user_id_input = input("\nEnter your user ID (usually 1 for first user): ")
    
    try:
        user_id = int(user_id_input)
        reset_and_rebuild(user_id)
    except ValueError:
        print("Invalid user ID. Please enter a number.")
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
