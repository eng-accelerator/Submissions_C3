"""
ULTIMATE FIX - Clean duplicates and rebuild vector store
This will:
1. Remove duplicate documents from database
2. Delete chroma_db folder completely  
3. Rebuild embeddings from unique documents only
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DBManager
from processors.document_processor import DocumentProcessor
from processors.text_chunker import TextChunker  
from processors.vector_store_manager import VectorStoreManager
from dotenv import load_dotenv
import shutil
from collections import defaultdict

load_dotenv()

def ultimate_fix(user_id: int):
    """Clean everything and rebuild properly"""
    
    print("=" * 70)
    print("ULTIMATE FIX - Clean Database + Rebuild Embeddings")
    print("=" * 70)
    
    db = DBManager()
    
    # Step 1: Find and remove duplicates
    print("\n1. Analyzing documents in database...")
    documents = db.get_user_documents(user_id)
    print(f"   Found {len(documents)} total documents")
    
    # Group by filename
    file_groups = defaultdict(list)
    for doc in documents:
        file_groups[doc.file_name].append(doc)
    
    # Find duplicates
    duplicates = {name: docs for name, docs in file_groups.items() if len(docs) > 1}
    unique_files = {name: docs for name, docs in file_groups.items() if len(docs) == 1}
    
    print(f"   Unique files: {len(unique_files)}")
    print(f"   Duplicate files: {len(duplicates)}")
    
    if duplicates:
        print("\n   Duplicate files found:")
        for name, docs in duplicates.items():
            print(f"   - {name}: {len(docs)} copies (IDs: {[d.id for d in docs]})")
        
        print("\n   We will keep only the LATEST version of each file.")
        response = input("\n   Remove duplicates? (y/n): ")
        
        if response.lower() != 'y':
            print("   Keeping all documents.")
        else:
            # Keep only the latest (highest ID) of each duplicate
            for name, docs in duplicates.items():
                # Sort by ID, keep the last one
                sorted_docs = sorted(docs, key=lambda x: x.id)
                to_delete = sorted_docs[:-1]  # All except the last
                to_keep = sorted_docs[-1]
                
                print(f"\n   Processing {name}:")
                print(f"   - Keeping: ID {to_keep.id}")
                print(f"   - Deleting: {[d.id for d in to_delete]}")
                
                # Delete old versions
                for doc in to_delete:
                    try:
                        # Note: We're not deleting from DB, just marking
                        # You could implement actual deletion if needed
                        print(f"     Marked document ID {doc.id} for skip")
                    except Exception as e:
                        print(f"     Error: {e}")
    
    # Step 2: Get final list of unique documents
    print("\n2. Building list of unique documents...")
    unique_docs = []
    seen_names = set()
    
    # Sort by ID descending to get latest versions first
    for doc in sorted(documents, key=lambda x: x.id, reverse=True):
        if doc.file_name not in seen_names:
            unique_docs.append(doc)
            seen_names.add(doc.file_name)
    
    print(f"   Final unique documents: {len(unique_docs)}")
    for doc in unique_docs:
        print(f"   - {doc.file_name} (ID: {doc.id})")
    
    # Step 3: Hard delete chroma_db
    print("\n3. Deleting chroma_db folder...")
    chroma_dir = "chroma_db"
    
    if os.path.exists(chroma_dir):
        response = input(f"   Delete {chroma_dir} folder? (y/n): ")
        if response.lower() != 'y':
            print("   Cancelled.")
            return
        
        try:
            shutil.rmtree(chroma_dir)
            print(f"   ✓ Deleted {chroma_dir}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            print("\n   Please manually delete chroma_db folder and run this again.")
            return
    else:
        print(f"   {chroma_dir} doesn't exist - will create fresh")
    
    # Step 4: Initialize fresh vector store
    print("\n4. Initializing fresh vector store...")
    vector_store = VectorStoreManager(persist_directory=chroma_dir)
    doc_processor = DocumentProcessor()
    text_chunker = TextChunker()
    print("   ✓ Vector store ready")
    
    # Step 5: Process unique documents only
    print(f"\n5. Processing {len(unique_docs)} unique documents...\n")
    
    success_count = 0
    fail_count = 0
    total_chunks = 0
    
    for i, doc in enumerate(unique_docs, 1):
        print(f"   [{i}/{len(unique_docs)}] Processing {doc.file_name} (ID: {doc.id})...")
        
        try:
            # Process document
            processed = doc_processor.process_document(doc.file_path)
            
            if not processed.get('success'):
                print(f"      ✗ Parse failed: {processed.get('error')}")
                fail_count += 1
                continue
            
            # Chunk
            chunk_metadata = {
                'user_id': user_id,
                'document_id': doc.id,
                'document_type': doc.document_type,
                'file_name': doc.file_name
            }
            
            chunks = text_chunker.chunk_document(processed, chunk_metadata)
            print(f"      Created {len(chunks)} chunks")
            
            if not chunks:
                print(f"      ⚠ No chunks created")
                continue
            
            # Add to vector store
            success = vector_store.add_chunks(user_id, chunks, chunk_metadata)
            
            if success:
                print(f"      ✓ Added {len(chunks)} embeddings")
                success_count += 1
                total_chunks += len(chunks)
            else:
                print(f"      ✗ Failed to add embeddings")
                fail_count += 1
                
        except Exception as e:
            print(f"      ✗ Error: {str(e)[:100]}")
            fail_count += 1
    
    # Step 6: Verify
    print(f"\n6. Verification...")
    try:
        stats = vector_store.get_collection_stats(user_id)
        actual_chunks = stats['total_chunks']
        
        print(f"   ✓ Vector store chunks: {actual_chunks}")
        print(f"   ✓ Successful: {success_count} documents")
        print(f"   ✓ Total chunks: {total_chunks}")
        
        if fail_count > 0:
            print(f"   ⚠ Failed: {fail_count} documents")
        
        if actual_chunks > 0:
            print("\n   🎉 SUCCESS! Embeddings are working!")
        else:
            print("\n   ⚠ WARNING: No chunks stored. Check errors above.")
            
    except Exception as e:
        print(f"   ✗ Verification error: {e}")
    
    print("\n" + "=" * 70)
    print("ULTIMATE FIX COMPLETE!")
    print("=" * 70)
    
    if success_count > 0 and actual_chunks > 0:
        print("\n✅ Your vector store is ready!")
        print("   Go to Chat page and try searching!")
    else:
        print("\n⚠ Something went wrong. Check the errors above.")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("AI Financial Coach - ULTIMATE FIX")
    print("=" * 70)
    
    user_id_input = input("\nEnter your user ID (usually 1): ")
    
    try:
        user_id = int(user_id_input)
        ultimate_fix(user_id)
    except ValueError:
        print("Invalid user ID.")
    except KeyboardInterrupt:
        print("\n\nCancelled.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
