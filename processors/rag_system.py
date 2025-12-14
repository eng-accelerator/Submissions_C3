import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from database.db_manager import DBManager
from processors.document_processor import DocumentProcessor
from processors.text_chunker import TextChunker
from processors.vector_store_manager import VectorStoreManager

class RAGSystem:
    """Coordinate document processing, chunking, embedding, and retrieval"""
    
    def __init__(self, db_manager: DBManager = None, openai_api_key: str = None):
        self.db = db_manager or DBManager()
        self.doc_processor = DocumentProcessor()
        self.text_chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
        self.vector_store = VectorStoreManager(
            persist_directory="chroma_db",
            openai_api_key=openai_api_key
        )
    
    def process_uploaded_document(self, user_id: int, file_path: str, 
                                  document_type: str, file_name: str) -> Dict[str, Any]:
        """Complete pipeline: process -> chunk -> embed -> store"""
        result = {
            'success': False,
            'message': '',
            'document_id': None,
            'chunks_created': 0,
            'vectors_created': 0
        }
        
        try:
            # Step 1: Process document
            print(f"Processing document: {file_name}")
            processed_doc = self.doc_processor.process_document(file_path)
            
            if not processed_doc.get('success'):
                result['message'] = f"Document processing failed: {processed_doc.get('error', 'Unknown error')}"
                return result
            
            # Step 2: Save document metadata to database
            doc_metadata = {
                'file_type': processed_doc.get('file_type'),
                'processing_date': datetime.utcnow().isoformat(),
                'pages': processed_doc.get('metadata', {}).get('num_pages'),
                'has_tables': len(processed_doc.get('metadata', {}).get('tables', [])) > 0
            }
            
            db_document = self.db.add_document(
                user_id=user_id,
                document_type=document_type,
                file_name=file_name,
                file_path=file_path,
                metadata=doc_metadata
            )
            
            if not db_document:
                result['message'] = "Failed to save document to database"
                return result
            
            result['document_id'] = db_document.id
            
            # Step 3: Chunk the document
            print(f"Chunking document...")
            chunk_metadata = {
                'user_id': user_id,
                'document_id': db_document.id,
                'document_type': document_type,
                'file_name': file_name,
                'upload_date': datetime.utcnow().isoformat()
            }
            
            chunks = self.text_chunker.chunk_document(processed_doc, chunk_metadata)
            
            if not chunks:
                result['message'] = "No text chunks created from document"
                result['success'] = True  # Document saved but no content to embed
                return result
            
            result['chunks_created'] = len(chunks)
            print(f"Created {len(chunks)} chunks")
            
            # Step 4: Embed and store chunks
            print(f"Creating embeddings and storing in vector database...")
            embedding_success = self.vector_store.add_chunks(
                user_id=user_id,
                chunks=chunks,
                document_metadata=chunk_metadata
            )
            
            if not embedding_success:
                result['message'] = "Failed to create embeddings"
                return result
            
            result['vectors_created'] = len(chunks)
            
            # Step 5: Extract and store structured financial data
            print(f"Extracting financial data...")
            financial_data = self.doc_processor.extract_financial_data(processed_doc, document_type)
            
            for data_item in financial_data:
                self.db.add_financial_data(
                    user_id=user_id,
                    data_type=data_item.get('type', 'unknown'),
                    category=data_item.get('category', 'Other'),
                    amount=data_item.get('amount', 0.0),
                    description=data_item.get('description', ''),
                    source_document_id=db_document.id
                )
            
            # Mark document as processed
            self.db.session.query(self.db.session.query(type(db_document)).filter_by(id=db_document.id).first().__class__)\
                .filter_by(id=db_document.id)\
                .update({'processed': True})
            self.db.session.commit()
            
            result['success'] = True
            result['message'] = f"Document processed successfully! Created {len(chunks)} chunks and {len(financial_data)} financial records."
            
            return result
        
        except Exception as e:
            result['message'] = f"Error in processing pipeline: {str(e)}"
            print(f"RAG System Error: {e}")
            return result
    
    def query_documents(self, user_id: int, query: str, 
                       document_type: str = None, k: int = 5) -> List[Dict[str, Any]]:
        """Query user's documents using RAG"""
        try:
            # Search vector store
            results = self.vector_store.search_with_score(
                user_id=user_id,
                query=query,
                k=k,
                filter_metadata={'document_type': document_type} if document_type else None
            )
            
            return results
        
        except Exception as e:
            print(f"Error querying documents: {e}")
            return []
    
    def get_context_for_query(self, user_id: int, query: str, 
                             document_type: str = None, max_tokens: int = 3000) -> str:
        """Get relevant context for a query"""
        return self.vector_store.get_relevant_context(
            user_id=user_id,
            query=query,
            document_type=document_type,
            max_tokens=max_tokens
        )
    
    def delete_document(self, user_id: int, document_id: int) -> bool:
        """Delete a document and its vectors"""
        try:
            # Delete from vector store
            self.vector_store.delete_document(user_id, document_id)
            
            # Delete from database (handled by db_manager if implemented)
            # For now, just mark as deleted or remove
            
            return True
        
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get statistics about user's documents"""
        try:
            # Get database stats
            documents = self.db.get_user_documents(user_id)
            
            # Get vector store stats
            vector_stats = self.vector_store.get_collection_stats(user_id)
            
            return {
                'total_documents': len(documents),
                'total_chunks': vector_stats.get('total_chunks', 0),
                'documents_by_type': self._count_by_type(documents),
                'processed_documents': sum(1 for doc in documents if doc.processed)
            }
        
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {
                'total_documents': 0,
                'total_chunks': 0,
                'documents_by_type': {},
                'processed_documents': 0
            }
    
    def _count_by_type(self, documents: List) -> Dict[str, int]:
        """Count documents by type"""
        counts = {}
        for doc in documents:
            doc_type = doc.document_type
            counts[doc_type] = counts.get(doc_type, 0) + 1
        return counts
    
    def reprocess_document(self, user_id: int, document_id: int) -> Dict[str, Any]:
        """Reprocess an existing document"""
        try:
            # Get document from database
            documents = self.db.get_user_documents(user_id)
            document = next((doc for doc in documents if doc.id == document_id), None)
            
            if not document:
                return {'success': False, 'message': 'Document not found'}
            
            # Delete old vectors
            self.vector_store.delete_document(user_id, document_id)
            
            # Reprocess
            return self.process_uploaded_document(
                user_id=user_id,
                file_path=document.file_path,
                document_type=document.document_type,
                file_name=document.file_name
            )
        
        except Exception as e:
            return {'success': False, 'message': f'Reprocessing failed: {str(e)}'}