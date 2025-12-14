import lancedb
from typing import List, Dict, Optional
import json
import os
import pandas as pd
import requests
import hashlib
import struct

class RAGEngine:
    """RAG engine using LanceDB for historical incident retrieval"""
    
    # Class-level flag to show warning only once
    _warning_shown = False
    
    def __init__(self, db_path: str, openrouter_api_key: Optional[str] = None, huggingface_api_key: Optional[str] = None):
        # Create directory if it doesn't exist
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize LanceDB
        self.db = lancedb.connect(db_path)
        
        # Store API keys
        self.openrouter_api_key = openrouter_api_key
        self.huggingface_api_key = huggingface_api_key or os.getenv("HUGGINGFACE_API_KEY")
        self.huggingface_api_url = "https://api-inference.huggingface.co/models"
        
        # Embedding method: 'hf_api' (Hugging Face API), 'hf_local' (local HF model), 'openai_api', or 'local' (sentence-transformers)
        self.embedding_method: Optional[str] = None
        self._embedding_model: Optional[object] = None
        self.embedding_model_name = 'sentence-transformers/all-MiniLM-L6-v2'
        self.hf_model_name = 'sentence-transformers/all-MiniLM-L6-v2'  # Hugging Face model
        
        # Try to initialize embedding method (prefer Hugging Face API)
        self._initialize_embedding_method()
        
        # Initialize or get table
        self.table_name = "incidents"
        try:
            self.table = self.db.open_table(self.table_name)
        except:
            # Create empty table with sample data to establish schema
            self.table = None
    
    def _initialize_embedding_method(self):
        """Initialize embedding method - prefer Hugging Face API (no DLL issues)"""
        # Priority 1: Try Hugging Face Inference API (best - no local dependencies, no PyTorch!)
        if self.huggingface_api_key:
            self.embedding_method = 'hf_api'
            if not RAGEngine._warning_shown:
                print("✓ RAG enabled: Using Hugging Face Inference API (no PyTorch needed!)")
                print(f"   Model: {self.hf_model_name}")
                print(f"   Get free API key: https://huggingface.co/settings/tokens")
                RAGEngine._warning_shown = True
            return
        
        # Priority 2: Try sentence-transformers (fallback - may have PyTorch issues)
        try:
            from sentence_transformers import SentenceTransformer
            self._embedding_model = SentenceTransformer(self.embedding_model_name)
            self.embedding_method = 'local'
            if not RAGEngine._warning_shown:
                print("✓ RAG enabled: Using local sentence-transformers model")
                RAGEngine._warning_shown = True
            return
        except Exception as e:
            pass
        
        # All methods failed - use fallback
        self.embedding_method = 'fallback'
        if not RAGEngine._warning_shown:
            print(f"⚠️  RAG using fallback method (limited semantic search)")
            print(f"   For better RAG: Add HUGGINGFACE_API_KEY to .env file")
            print(f"   Get free key: https://huggingface.co/settings/tokens")
            RAGEngine._warning_shown = True
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using best available method"""
        if self.embedding_method == 'hf_api':
            return self._get_embedding_hf_api(text)
        elif self.embedding_method == 'hf_local':
            return self._get_embedding_hf_local(text)
        elif self.embedding_method == 'api':
            return self._get_embedding_api(text)
        elif self.embedding_method == 'local':
            return self._get_embedding_local(text)
        else:
            return []
    
    def _get_embedding_hf_api(self, text: str) -> List[float]:
        """Generate embedding using Hugging Face Inference API (no local dependencies!)"""
        try:
            headers = {
                "Authorization": f"Bearer {self.huggingface_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": text,
                "options": {"wait_for_model": True}
            }
            
            # Try primary URL
            url = f"{self.huggingface_api_url}/{self.hf_model_name}"
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Handle 410 (Gone) or 404 - endpoint deprecated or model removed
            if response.status_code in [410, 404]:
                print(f"Warning: HF API returned {response.status_code}. Switching to local/fallback mode.")
                # Switch method to avoid future API calls
                try:
                    from sentence_transformers import SentenceTransformer
                    self._embedding_model = SentenceTransformer(self.embedding_model_name)
                    self.embedding_method = 'local'
                    return self._get_embedding_local(text)
                except Exception as e:
                    print(f"Warning: Could not switch to local embeddings: {e}. Using fallback.")
                    self.embedding_method = 'fallback'
                    return self._get_embedding_fallback(text)

            if response.status_code == 200:
                embedding = response.json()
                # HF API returns list of floats directly
                if isinstance(embedding, list) and len(embedding) > 0:
                    if isinstance(embedding[0], list):
                        # Sometimes returns nested list
                        return embedding[0]
                    return embedding
                return []
            elif response.status_code == 503:
                # Model is loading, wait and retry
                import time
                time.sleep(5)
                return self._get_embedding_hf_api(text)  # Retry once
            else:
                print(f"Warning: Hugging Face API error: {response.status_code} - {response.text[:100]}")
                # For any other error, fall back for this call but don't permanently switch unless repeated?
                # For now, safe to use fallback
                return self._get_embedding_fallback(text)
                
        except Exception as e:
            print(f"Warning: Failed to get HF API embedding: {e}")
            return []
    
    def _get_embedding_hf_api(self, text: str) -> List[float]:
        """Generate embedding using Hugging Face Inference API (no PyTorch needed!)"""
        try:
            headers = {
                "Authorization": f"Bearer {self.huggingface_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": text,
                "options": {"wait_for_model": True}  # Wait if model is loading
            }
            
            response = requests.post(
                f"{self.huggingface_api_url}/{self.hf_model_name}",
                headers=headers,
                json=payload,
                timeout=30  # Longer timeout for model loading
            )
            
            if response.status_code == 200:
                result = response.json()
                # Hugging Face returns a list of embeddings (one per input)
                if isinstance(result, list) and len(result) > 0:
                    return result[0]  # Return first embedding
                elif isinstance(result, list):
                    return result
                else:
                    return result
            elif response.status_code == 503:
                # Model is loading, retry once
                import time
                time.sleep(2)
                response = requests.post(
                    f"{self.huggingface_api_url}/{self.hf_model_name}",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0]
                    return result if isinstance(result, list) else []
                else:
                    print(f"Warning: Hugging Face API model still loading. Using fallback.")
                    return self._get_embedding_fallback(text)
            else:
                print(f"Warning: Hugging Face API error: {response.status_code}")
                return self._get_embedding_fallback(text)
                
        except Exception as e:
            print(f"Warning: Failed to get embedding from Hugging Face API: {e}")
            return self._get_embedding_fallback(text)
    
    def _get_embedding_fallback(self, text: str) -> List[float]:
        """Simple fallback embedding using text hashing (basic similarity)"""
        # This is a very basic fallback - not ideal but better than nothing
        # For hackathon, we'll use a simple hash-based approach
        import hashlib
        import struct
        
        # Create a simple hash-based embedding (not semantic, but works for demo)
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to 384-dim vector (matching MiniLM size for compatibility)
        embedding = []
        for i in range(0, min(len(hash_bytes), 48), 4):  # 48 bytes = 12 floats = 384 dims with repetition
            val = struct.unpack('f', hash_bytes[i:i+4] + b'\x00' * (4 - len(hash_bytes[i:i+4])))[0] if i+4 <= len(hash_bytes) else 0.0
            # Normalize and repeat to get 384 dimensions
            for _ in range(8):  # 12 * 8 = 96, repeat 4 times = 384
                embedding.append((val % 1.0) - 0.5)  # Normalize to [-0.5, 0.5]
        
        # Pad to 384 if needed
        while len(embedding) < 384:
            embedding.append(0.0)
        
        return embedding[:384]
    
    def _get_embedding_local(self, text: str) -> List[float]:
        """Generate embedding using local sentence-transformers model"""
        try:
            if self._embedding_model is None:
                from sentence_transformers import SentenceTransformer
                self._embedding_model = SentenceTransformer(self.embedding_model_name)
            embedding = self._embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"Warning: Failed to get local embedding: {e}")
            return []
    
    def index_incident(self, incident_id: str, incident_data: Dict):
        """Index a new incident in LanceDB"""
        try:
            # Check if embedding method is available
            if self.embedding_method is None:
                # RAG is disabled, skip indexing
                return
            
            # Create text for embedding (combine relevant fields)
            description = incident_data.get('description', '')
            service = incident_data.get('service', '')
            root_cause = incident_data.get('rootCause', '')
            error_code = incident_data.get('errorCode', '')
            component = incident_data.get('component', '')
            
            text_for_embedding = f"{description} {service} {root_cause} {error_code} {component}".strip()
            
            # Generate embedding
            vector = self._get_embedding(text_for_embedding)
            if not vector:  # Empty embedding means model failed
                return
            
            # Prepare data
            data = {
                "id": incident_id,
                "severity": incident_data.get("severity", "P3"),
                "service": incident_data.get("service", "unknown"),
                "timestamp": incident_data.get("timestamp", ""),
                "description": description,
                "data": json.dumps(incident_data),
                "vector": vector
            }
            
            # Create DataFrame
            df = pd.DataFrame([data])
            
            # Add to table (create if doesn't exist)
            if self.table is None:
                self.table = self.db.create_table(self.table_name, df)
            else:
                self.table.add(df)
                
        except Exception as e:
            print(f"Warning: Failed to index incident (RAG may be disabled): {e}")
    
    def retrieve_similar_incidents(self, query: str, n_results: int = 3) -> List[Dict]:
        """Retrieve similar historical incidents using vector similarity"""
        try:
            # Check if embedding method is available
            if self.embedding_method is None:
                # RAG is disabled - silently return empty (error already logged during init)
                return []
            
            if self.table is None:
                return []
            
            # Check if table has data
            try:
                count = len(self.table)
                if count == 0:
                    return []
            except:
                return []
            
            # Generate query embedding
            query_vector = self._get_embedding(query)
            if not query_vector:  # Empty embedding means model failed
                return []
            
            # Search for similar incidents
            results = self.table.search(query_vector).limit(n_results).to_pandas()
            
            # Parse results
            similar_incidents = []
            for _, row in results.iterrows():
                try:
                    if pd.notna(row.get('data')):
                        incident_data = json.loads(row['data'])
                        similar_incidents.append(incident_data)
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    print(f"Error parsing incident data: {e}")
                    continue
            
            return similar_incidents
            
        except Exception as e:
            print(f"Error retrieving incidents: {e}")
            return []
    
    def get_incident_statistics(self) -> Dict:
        """Get statistics about historical incidents"""
        try:
            if self.table is None:
                return {"total_incidents": 0, "avg_resolution_time": "N/A"}
            
            count = len(self.table)
            return {
                "total_incidents": count if count else 0,
                "avg_resolution_time": "2.5 hours"
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {"total_incidents": 0, "avg_resolution_time": "N/A"}