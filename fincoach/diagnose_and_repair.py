"""
Diagnostic and Repair Script for Document Embeddings
Run this to check and fix vector store issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DBManager
from processors.rag_system import RAGSystem
from dotenv import load_dotenv

load_dotenv()

def diagnose_and_repair(user_id: int):
    """Diagnose and repair vector store issues"""
    
    print("=" * 60)
    print("DIAGNOSTIC AND REPAIR SCRIPT")
    print("=" * 60)
    
    db = DBManager()
    rag = RAGSystem(db_manager=db)
    
    # Step 1: Check database
    print("\n1. Checking Database...")
    documents = db.get_user_documents(user_id)
    print(f"   ✓ Found {len(documents)} documents in database")
    
    for doc in documents:
        print(f"   - {doc.file_name} (Type: {doc.document_type}, Processed: {doc.processed})")
    
    # Step 2: Check vector store
    print("\n2. Checking Vector Store...")
    try:
        stats = rag.vector_store.get_collection_stats(user_id)
        print(f"   ✓ Vector store has {stats['total_chunks']} chunks")
    except Exception as e:
        print(f"   ✗ Error accessing vector store: {e}")
        stats = {'total_chunks': 0}
    
    # Step 3: Check financial data
    print("\n3. Checking Financial Data...")
    financial_data = db.get_financial_data(user_id)
    print(f"   ✓ Found {len(financial_data)} financial records")
    
    for data in financial_data[:5]:  # Show first 5
        print(f"   - {data.data_type}: {data.category} = ₹{data.amount:,.2f}")
    
    # Step 4: Repair if needed
    if stats['total_chunks'] == 0 and len(documents) > 0:
        print("\n4. REPAIR NEEDED: Documents exist but no chunks in vector store")
        print("   Would you like to reprocess all documents? (y/n)")
        
        response = input("   > ")
        
        if response.lower() == 'y':
            print("\n   Reprocessing all documents...")
            for i, doc in enumerate(documents, 1):
                print(f"\n   [{i}/{len(documents)}] Processing {doc.file_name}...")
                try:
                    result = rag.reprocess_document(user_id, doc.id)
                    if result['success']:
                        print(f"      ✓ Success: {result['message']}")
                        print(f"      ✓ Created {result.get('chunks_created', 0)} chunks")
                    else:
                        print(f"      ✗ Failed: {result['message']}")
                except Exception as e:
                    print(f"      ✗ Error: {e}")
            
            print("\n   Reprocessing complete!")
            
            # Recheck stats
            stats = rag.vector_store.get_collection_stats(user_id)
            print(f"\n   New vector store stats: {stats['total_chunks']} chunks")
        else:
            print("   Skipping repair.")
    else:
        print("\n4. No repair needed - everything looks good!")
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    # Get user ID
    user_id = input("Enter your user ID (check Profile page or use 1 for first user): ")
    
    try:
        user_id = int(user_id)
        diagnose_and_repair(user_id)
    except ValueError:
        print("Invalid user ID. Please enter a number.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
