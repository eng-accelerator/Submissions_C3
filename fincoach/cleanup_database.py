"""
Database Cleanup - Remove Duplicate Documents
This will clean up the documents table keeping only the latest version of each file
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DBManager
from sqlalchemy import text
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

def cleanup_duplicates(user_id: int):
    """Remove duplicate documents from database"""
    
    print("=" * 70)
    print("DATABASE CLEANUP - Remove Duplicate Documents")
    print("=" * 70)
    
    db = DBManager()
    
    # Step 1: Get all documents
    print("\n1. Analyzing documents...")
    documents = db.get_user_documents(user_id)
    print(f"   Total documents in database: {len(documents)}")
    
    # Group by filename
    file_groups = defaultdict(list)
    for doc in documents:
        file_groups[doc.file_name].append(doc)
    
    # Find duplicates
    unique_count = sum(1 for docs in file_groups.values() if len(docs) == 1)
    duplicate_count = sum(1 for docs in file_groups.values() if len(docs) > 1)
    
    print(f"   Unique files: {unique_count}")
    print(f"   Files with duplicates: {duplicate_count}")
    
    if duplicate_count == 0:
        print("\n   No duplicates found! Database is clean.")
        return
    
    # Step 2: Show duplicates
    print("\n2. Duplicate files:")
    total_to_delete = 0
    for filename, docs in file_groups.items():
        if len(docs) > 1:
            sorted_docs = sorted(docs, key=lambda x: x.id)
            print(f"\n   {filename}: {len(docs)} copies")
            print(f"   - IDs: {[d.id for d in sorted_docs]}")
            print(f"   - Will keep: ID {sorted_docs[-1].id} (latest)")
            print(f"   - Will delete: {[d.id for d in sorted_docs[:-1]]}")
            total_to_delete += len(docs) - 1
    
    print(f"\n   Total documents to delete: {total_to_delete}")
    print(f"   Documents to keep: {len(file_groups)}")
    
    # Step 3: Confirm deletion
    response = input("\n   Proceed with cleanup? (y/n): ")
    if response.lower() != 'y':
        print("   Cancelled.")
        return
    
    # Step 4: Delete duplicates
    print("\n3. Deleting duplicate documents...")
    deleted_count = 0
    
    for filename, docs in file_groups.items():
        if len(docs) > 1:
            # Sort by ID, delete all except the last (latest)
            sorted_docs = sorted(docs, key=lambda x: x.id)
            to_delete = sorted_docs[:-1]
            
            for doc in to_delete:
                try:
                    # Delete from database
                    db.session.execute(
                        text("DELETE FROM documents WHERE id = :doc_id"),
                        {"doc_id": doc.id}
                    )
                    deleted_count += 1
                    print(f"   ✓ Deleted document ID {doc.id} ({doc.file_name})")
                except Exception as e:
                    print(f"   ✗ Error deleting ID {doc.id}: {e}")
    
    # Commit changes
    try:
        db.session.commit()
        print(f"\n   ✓ Successfully deleted {deleted_count} duplicate documents")
    except Exception as e:
        db.session.rollback()
        print(f"\n   ✗ Error committing changes: {e}")
        return
    
    # Step 5: Verify
    print("\n4. Verification...")
    remaining_docs = db.get_user_documents(user_id)
    print(f"   Documents remaining: {len(remaining_docs)}")
    
    # Show remaining documents
    print("\n   Final document list:")
    for doc in remaining_docs:
        status = "✅ Processed" if doc.processed else "⏳ Pending"
        print(f"   - {doc.file_name} (ID: {doc.id}) {status}")
    
    print("\n" + "=" * 70)
    print("CLEANUP COMPLETE!")
    print("=" * 70)
    print(f"\n✅ Database cleaned! {deleted_count} duplicates removed.")
    print(f"📄 {len(remaining_docs)} unique documents remain.")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("AI Financial Coach - Database Cleanup Tool")
    print("=" * 70)
    
    user_id_input = input("\nEnter your user ID (usually 1): ")
    
    try:
        user_id = int(user_id_input)
        cleanup_duplicates(user_id)
        print("\n💡 Tip: Restart Streamlit to see the changes in the UI")
    except ValueError:
        print("Invalid user ID.")
    except KeyboardInterrupt:
        print("\n\nCancelled.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
