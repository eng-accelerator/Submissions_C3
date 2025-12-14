"""
Diagnostic Script - Check Document Processing Status
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.models import SessionLocal, Document, FinancialData
from processors.rag_system import RAGSystem
from processors.document_processor import DocumentProcessor

def diagnose_documents(user_id: int):
    """Check what's happening with document processing"""
    
    session = SessionLocal()
    
    print("="*80)
    print(f"DOCUMENT PROCESSING DIAGNOSTIC - User ID: {user_id}")
    print("="*80)
    
    # Get all documents
    docs = session.query(Document).filter(Document.user_id == user_id).all()
    
    print(f"\nTotal Documents: {len(docs)}")
    print("-"*80)
    
    for doc in docs:
        print(f"\n📄 {doc.file_name}")
        print(f"   Type: {doc.document_type}")
        print(f"   Processed: {'✅ Yes' if doc.processed else '❌ No'}")
        print(f"   File Path: {doc.file_path}")
        print(f"   Uploaded: {doc.uploaded_at}")
        
        # Check if file exists
        if os.path.exists(doc.file_path):
            print(f"   File Exists: ✅ Yes ({os.path.getsize(doc.file_path)} bytes)")
        else:
            print(f"   File Exists: ❌ No - FILE MISSING!")
        
        # Check financial data extracted
        financial_data = session.query(FinancialData).filter(
            FinancialData.source_document_id == doc.id
        ).all()
        
        print(f"   Financial Data: {len(financial_data)} records")
        
        if financial_data:
            print(f"\n   Extracted Data:")
            for fd in financial_data[:5]:  # Show first 5
                print(f"      - {fd.data_type.upper()}: {fd.category} = ₹{fd.amount:,.2f}")
            
            if len(financial_data) > 5:
                print(f"      ... and {len(financial_data) - 5} more")
        else:
            print(f"   ⚠️  NO FINANCIAL DATA EXTRACTED!")
            
            # Try to process now and see what happens
            if os.path.exists(doc.file_path):
                print(f"\n   🔍 Testing extraction now...")
                try:
                    processor = DocumentProcessor()
                    processed_doc = processor.process_document(doc.file_path)
                    
                    if processed_doc.get('success'):
                        print(f"      Document processed successfully")
                        print(f"      Full text length: {len(processed_doc.get('full_text', ''))} chars")
                        
                        # Try extraction
                        extracted = processor.extract_financial_data(processed_doc, doc.document_type)
                        
                        print(f"      Extraction result: {len(extracted)} records")
                        
                        if extracted:
                            print(f"      Sample extracted data:")
                            for item in extracted[:3]:
                                print(f"         - {item.get('type')}: {item.get('category')} = ₹{item.get('amount', 0):,.2f}")
                        else:
                            print(f"      ❌ No data extracted!")
                            print(f"      Document type: {doc.document_type}")
                            print(f"      First 500 chars of text:")
                            print(f"      {processed_doc.get('full_text', '')[:500]}")
                    else:
                        print(f"      ❌ Document processing failed: {processed_doc.get('error')}")
                
                except Exception as e:
                    print(f"      ❌ Error during test: {e}")
                    import traceback
                    traceback.print_exc()
        
        print("-"*80)
    
    session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Diagnose document processing')
    parser.add_argument('user_id', type=int, help='User ID to check')
    
    args = parser.parse_args()
    
    diagnose_documents(args.user_id)
