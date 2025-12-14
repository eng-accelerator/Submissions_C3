import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import time

# Fix for langchain document import
try:
    from langchain.docstore.document import Document as LangchainDocument
except ImportError:
    try:
        from langchain_core.documents import Document as LangchainDocument
    except ImportError:
        class LangchainDocument:
            def __init__(self, page_content: str, metadata: dict = None):
                self.page_content = page_content
                self.metadata = metadata or {}

import json

class VectorStoreManager:
    """Manage vector embeddings and retrieval using ChromaDB with local embeddings"""
    
    def __init__(self, persist_directory: str = "chroma_db", openai_api_key: str = None):
        self.persist_directory = persist_directory
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Use ChromaDB's built-in sentence transformer embeddings (no API needed!)
        try:
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"  # Small, fast, local model
            )
            print("Using local sentence-transformers embeddings (no API key needed)")
        except Exception as e:
            print(f"Error initializing embeddings: {e}")
            print("Trying default embedding function...")
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Initialize ChromaDB client
        try:
            self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")
            raise
        
        # Store for user collections
        self.user_collections = {}
    
    def get_user_collection_name(self, user_id: int) -> str:
        """Get collection name for a user"""
        return f"user_{user_id}_docs_v2"
    
    def get_or_create_collection(self, user_id: int):
        """Get or create a ChromaDB collection for a user - PRESERVES existing data"""
        collection_name = self.get_user_collection_name(user_id)
        
        if collection_name not in self.user_collections:
            try:
                # Try to GET existing collection first (don't delete!)
                try:
                    collection = self.chroma_client.get_collection(
                        name=collection_name,
                        embedding_function=self.embedding_function
                    )
                    print(f"Using existing collection: {collection_name} with {collection.count()} chunks")
                except:
                    # Collection doesn't exist, create it
                    collection = self.chroma_client.create_collection(
                        name=collection_name,
                        embedding_function=self.embedding_function,
                        metadata={"hnsw:space": "cosine"}
                    )
                    print(f"Created new collection: {collection_name}")
                
                self.user_collections[collection_name] = collection
            except Exception as e:
                print(f"Error with collection: {e}")
                raise
        
        return self.user_collections[collection_name]
    
    def add_chunks(self, user_id: int, chunks: List[Dict[str, Any]], document_metadata: Dict[str, Any] = None) -> bool:
        """Add text chunks to user's vector store"""
        try:
            collection = self.get_or_create_collection(user_id)
            
            # Prepare data for ChromaDB
            ids = []
            documents = []
            metadatas = []
            
            # Use timestamp to make IDs absolutely unique
            timestamp = int(time.time() * 1000)  # milliseconds
            
            for i, chunk in enumerate(chunks):
                # Create TRULY unique ID with timestamp
                chunk_id = chunk.get('chunk_id', i)
                doc_id = document_metadata.get('document_id', 0) if document_metadata else 0
                # Add timestamp and random component to guarantee uniqueness
                unique_id = f"doc_{doc_id}_chunk_{chunk_id}_t{timestamp}_{i}"
                ids.append(unique_id)
                
                # Get text
                documents.append(chunk['text'])
                
                # Combine metadata
                metadata = chunk.get('metadata', {}).copy()
                if document_metadata:
                    metadata.update(document_metadata)
                
                # Add chunk-specific info
                metadata['chunk_id'] = str(chunk.get('chunk_id', i))
                metadata['token_count'] = str(chunk.get('token_count', 0))
                metadata['char_count'] = str(chunk.get('char_count', 0))
                
                # Clean metadata - ChromaDB only accepts str, int, float, bool
                clean_metadata = {}
                for key, value in metadata.items():
                    if value is None:
                        continue
                    if isinstance(value, (str, int, float, bool)):
                        clean_metadata[key] = value
                    else:
                        clean_metadata[key] = str(value)
                
                metadatas.append(clean_metadata)
            
            # Add to collection - do it all at once
            try:
                collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                print(f"Successfully added {len(ids)} chunks to vector store")
                return True
                
            except Exception as add_error:
                print(f"Error adding to collection: {add_error}")
                return False
        
        except Exception as e:
            print(f"Error adding chunks to vector store: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def search_similar(self, user_id: int, query: str, k: int = 5, filter_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        try:
            collection = self.get_or_create_collection(user_id)
            
            # Prepare where filter
            where_filter = None
            if filter_metadata:
                where_filter = {}
                for key, value in filter_metadata.items():
                    where_filter[key] = value
            
            # Perform search
            results = collection.query(
                query_texts=[query],
                n_results=k,
                where=where_filter if where_filter else None
            )
            
            # Convert to dict format
            search_results = []
            if results and results['documents'] and len(results['documents']) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    search_results.append({
                        'content': doc,
                        'metadata': metadata
                    })
            
            return search_results
        
        except Exception as e:
            print(f"Error searching vector store: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def search_with_score(self, user_id: int, query: str, k: int = 5, filter_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search with similarity scores"""
        try:
            collection = self.get_or_create_collection(user_id)
            
            # Prepare where filter
            where_filter = None
            if filter_metadata:
                where_filter = {}
                for key, value in filter_metadata.items():
                    where_filter[key] = value
            
            # Perform search
            results = collection.query(
                query_texts=[query],
                n_results=k,
                where=where_filter if where_filter else None
            )
            
            # Convert to dict format
            search_results = []
            if results and results['documents'] and len(results['documents']) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 0
                    search_results.append({
                        'content': doc,
                        'metadata': metadata,
                        'similarity_score': distance
                    })
            
            return search_results
        
        except Exception as e:
            print(f"Error searching vector store with scores: {e}")
            return []
    
    def get_relevant_context(self, user_id: int, query: str, document_type: str = None, max_tokens: int = 3000) -> str:
        """Get relevant context for a query"""
        filter_metadata = {'document_type': document_type} if document_type else None
        
        results = self.search_with_score(user_id, query, k=10, filter_metadata=filter_metadata)
        
        # Sort by score
        results.sort(key=lambda x: x.get('similarity_score', float('inf')))
        
        # Combine results
        context_parts = []
        total_tokens = 0
        
        for result in results:
            content = result['content']
            tokens = int(result['metadata'].get('token_count', len(content) // 4))
            
            if total_tokens + tokens > max_tokens:
                break
            
            source = result['metadata'].get('source', 'Unknown')
            page = result['metadata'].get('page', '')
            page_info = f" (Page {page})" if page else ""
            
            context_parts.append(f"From {source}{page_info}:\n{content}")
            total_tokens += tokens
        
        return "\n\n---\n\n".join(context_parts)
    
    def delete_document(self, user_id: int, document_id: int) -> bool:
        """Delete all chunks for a specific document"""
        try:
            collection = self.get_or_create_collection(user_id)
            
            # Get all IDs for this document
            results = collection.get(
                where={"document_id": str(document_id)}
            )
            
            if results and results['ids']:
                collection.delete(ids=results['ids'])
            
            return True
        
        except Exception as e:
            print(f"Error deleting document from vector store: {e}")
            return False
    
    def get_collection_stats(self, user_id: int) -> Dict[str, Any]:
        """Get statistics about user's collection"""
        try:
            collection = self.get_or_create_collection(user_id)
            count = collection.count()
            
            return {
                'total_chunks': count,
                'collection_name': self.get_user_collection_name(user_id)
            }
        
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {'total_chunks': 0}
    
    def clear_user_collection(self, user_id: int) -> bool:
        """Clear all documents for a user"""
        try:
            collection_name = self.get_user_collection_name(user_id)
            self.chroma_client.delete_collection(collection_name)
            
            # Remove from cache
            if collection_name in self.user_collections:
                del self.user_collections[collection_name]
            
            return True
        
        except Exception as e:
            print(f"Error clearing user collection: {e}")
            return False