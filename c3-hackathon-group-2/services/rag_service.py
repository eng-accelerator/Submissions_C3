import os
import shutil
import warnings
from typing import List, Optional
from pathlib import Path

# Suppress benign torch/pydantic warnings
warnings.filterwarnings("ignore", message=".*torch.classes.*")
warnings.filterwarnings("ignore", category=FutureWarning)

# LlamaIndex Imports
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    ServiceContext,
    Settings,
    load_index_from_storage,
    Document
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.core.node_parser import SentenceSplitter

class RagService:
    """
    Service for RAG (Retrieval-Augmented Generation) operations using LlamaIndex.
    Handles document ingestion, indexing, and querying.
    """
    
    _instance = None
    _index = None
    
    # Configuration
    PERSIST_DIR = "./storage"
    UPLOAD_DIR = "./uploads"
    CHROMA_DB_PATH = "./chroma_db"
    COLLECTION_NAME = "finance_docs"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RagService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the RAG service with embeddings, LLM, and vector store."""
        
        # 1. Setup Directories
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.CHROMA_DB_PATH, exist_ok=True)
        
        # 2. Setup Embedding Model (HuggingFace - Local/Fast)
        # Using all-MiniLM-L6-v2 which is small and effective
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # 3. Setup LLM (OpenRouter via OpenAI compatible API)
        # Check for API Key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("WARNING: OPENROUTER_API_KEY not found. RAG queries will fail.")
            
        Settings.llm = OpenAI(
            model="gpt-4", # Cost-effective model
            api_key=api_key,
            api_base="https://openrouter.ai/api/v1",
            temperature=0.1,
            max_tokens=512
        )
        
        # 4. Setup Vector Store (ChromaDB)
        self.chroma_client = chromadb.PersistentClient(path=self.CHROMA_DB_PATH)
        self.chroma_collection = self.chroma_client.get_or_create_collection(self.COLLECTION_NAME)
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        
        # 5. Load Index (if exists) or create new
        try:
            self._index = VectorStoreIndex.from_vector_store(
                self.vector_store,
                storage_context=self.storage_context
            )
        except Exception as e:
            print(f"Index initialization note: {e}")
            self._index = None

    def process_file(self, file_content: bytes, file_name: str) -> bool:
        """
        Process an uploaded file: save it, ingest it, and update the index.
        """
        try:
            # 1. Save to temp file
            file_path = os.path.join(self.UPLOAD_DIR, file_name)
            with open(file_path, "wb") as f:
                f.write(file_content)
                
            # 2. Load document
            # SimpleDirectoryReader is robust for PDF, TXT, CSV
            documents = SimpleDirectoryReader(
                input_files=[file_path]
            ).load_data()
            
            # Add metadata
            for doc in documents:
                doc.metadata["file_name"] = file_name
            
            # 3. Update Index
            if self._index:
                # Insert details into existing index
                for doc in documents:
                    self._index.insert(doc)
            else:
                # Create fresh index
                self._index = VectorStoreIndex.from_documents(
                    documents, 
                    storage_context=self.storage_context
                )
            
            # 4. Persist
            # ChromaDB persists automatically, but good to ensure
            return True
            
        except Exception as e:
            print(f"Error processing file {file_name}: {e}")
            return False

    def query(self, question: str) -> str:
        """
        Query the documents.
        """
        if not self._index:
            return "No documents indexed yet. Please upload files first."
            
        try:
            query_engine = self._index.as_query_engine(
                streaming=False,
                similarity_top_k=3
            )
            response = query_engine.query(question)
            return str(response)
        except Exception as e:
            return f"Error occurred during query: {str(e)}"
    
    def get_indexed_docs(self) -> List[str]:
        """Return list of indexed document names."""
        # This is a bit tricky with Chroma/LlamaIndex abstraction
        # simpler to track via session state or database in MVP
        # But we can try to look at uploads folder
        return os.listdir(self.UPLOAD_DIR)

    def extract_financial_data(self, file_path: str) -> dict:
        """
        Extract structured financial data from a document using LLM.
        """
        try:
            # 1. Load document text
            docs = SimpleDirectoryReader(input_files=[file_path]).load_data()
            text_content = "\n".join([d.text for d in docs])[:10000] # Truncate for token limits
            
            # 2. Prompt for extraction
            prompt = f"""
            You are a financial data extraction AI. 
            Analyze the following document text and extract financial metrics into valid JSON format.
            Return ONLY the JSON object, no markdown formatting.
            
            Structure to extract:
            {{
                "snapshot": {{
                    "monthly_income": <number or 0>,
                    "monthly_expenses": <number or 0>,
                    "current_savings": <number or 0>
                }},
                "assets": [
                    {{ "type": "stock/mutual_fund/bank/real_estate/gold/other", "name": "<name>", "value": <number> }}
                ],
                "liabilities": [
                    {{ "type": "loan/credit_card/mortgage/other", "name": "<name>", "outstanding": <number>, "interest_rate": <decimal 0-1> }}
                ]
            }}
            
            Document Text:
            {text_content}
            """
            
            # 3. Call LLM
            response = Settings.llm.complete(prompt)
            response_text = str(response).strip()
            
            # 4. Parse JSON
            import json
            import re
            
            # Clean potential markdown code blocks
            json_str = re.sub(r'```json\s*|\s*```', '', response_text)
            return json.loads(json_str)
            
        except Exception as e:
            print(f"Extraction error: {e}")
            return {}

# Global instance
rag_service = RagService()
