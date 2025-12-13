components/rag_system.py

"""
Component 3: Vector Store & RAG System
Technology: FAISS + OpenRouter Embeddings
"""

import faiss
import numpy as np
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")
SITE_URL = os.getenv("SITE_URL", "http://localhost:8501")
APP_NAME = os.getenv("APP_NAME", "DesignAnalysisPoc")


def create_text_embedding(text):
    """
    Function 3.2: Generate embeddings using OpenRouter
    
    Args:
        text: Input text string
    
    Returns:
        np.array: 1536-dimensional embedding vector
    """
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": SITE_URL,
            "X-Title": APP_NAME,
            "Content-Type": "application/json"
        }
        
        data = {
            "model": EMBEDDING_MODEL,
            "input": text
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/embeddings",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            embedding = np.array(result['data'][0]['embedding'], dtype='float32')
            return embedding
        else:
            print(f"⚠️ Embedding API error: {response.status_code}")
            return np.zeros(1536, dtype='float32')
    
    except Exception as e:
        print(f"⚠️ Error creating embedding: {e}")
        return np.zeros(1536, dtype='float32')


def initialize_faiss_index(dimension=1536):
    """
    Function 3.1: Create FAISS index
    
    Args:
        dimension: Embedding dimension (1536 for OpenAI embeddings)
    
    Returns:
        faiss.Index: FAISS index object
    """
    # Use L2 distance (can switch to Inner Product for cosine similarity)
    index = faiss.IndexFlatL2(dimension)
    return index


def load_design_patterns_to_faiss(patterns_json_path):
    """
    Function 3.3: Load design patterns and create FAISS index
    
    Args:
        patterns_json_path: Path to design_patterns.json
    
    Returns:
        tuple: (faiss_index, metadata_list)
    """
    print("🔄 Loading design patterns into FAISS...")
    
    try:
        # Load patterns from JSON
        with open(patterns_json_path, 'r') as f:
            patterns = json.load(f)
        
        embeddings = []
        metadata = []
        
        # Create embeddings for each pattern
        for i, pattern in enumerate(patterns):
            # Combine title + description for better retrieval
            text = f"{pattern['title']}: {pattern['description']}"
            
            print(f"  Embedding pattern {i+1}/{len(patterns)}: {pattern['title']}")
            embedding = create_text_embedding(text)
            
            embeddings.append(embedding)
            metadata.append(pattern)
        
        # Create FAISS index
        embeddings_array = np.array(embeddings, dtype='float32')
        dimension = embeddings_array.shape[1]
        
        index = initialize_faiss_index(dimension)
        index.add(embeddings_array)
        
        print(f"✅ FAISS index created with {len(patterns)} patterns")
        return index, metadata
    
    except Exception as e:
        print(f"❌ Error loading patterns to FAISS: {e}")
        # Return empty index and metadata
        return initialize_faiss_index(1536), []


def retrieve_relevant_patterns(query, faiss_index, metadata, platform, top_k=5):
    """
    Function 3.4: Query FAISS for relevant design patterns
    
    Args:
        query: Search query string
        faiss_index: FAISS index object
        metadata: List of pattern metadata
        platform: Target platform (Instagram, Facebook, etc.)
        top_k: Number of results to return
    
    Returns:
        list: Relevant pattern dictionaries
    """
    if not metadata:
        return []
    
    try:
        # Create query embedding
        query_embedding = create_text_embedding(query)
        query_vector = np.array([query_embedding], dtype='float32')
        
        # Search FAISS
        distances, indices = faiss_index.search(query_vector, min(top_k * 2, len(metadata)))
        
        # Filter by platform
        results = []
        for idx in indices[0]:
            if idx < len(metadata):
                pattern = metadata[idx]
                platforms = pattern.get('platforms', [])
                
                # Check if platform matches
                if any(platform.lower() in p.lower() for p in platforms):
                    results.append(pattern)
                    if len(results) >= top_k:
                        break
        
        return results
    
    except Exception as e:
        print(f"⚠️ Error retrieving patterns: {e}")
        return []


def augment_prompt_with_rag(base_prompt, retrieved_patterns):
    """
    Function 3.5: Inject retrieved patterns into prompt
    
    Args:
        base_prompt: Original prompt string
        retrieved_patterns: List of pattern dicts from RAG
    
    Returns:
        str: Enhanced prompt with RAG context
    """
    if not retrieved_patterns:
        return base_prompt
    
    rag_context = "\n\n🔍 RELEVANT DESIGN PATTERNS FROM KNOWLEDGE BASE:\n"
    
    for i, pattern in enumerate(retrieved_patterns, 1):
        rag_context += f"""
{i}. **{pattern['title']}** (Category: {pattern['category']})
   Description: {pattern['description']}
   Best Practice: {pattern['best_practice']}
   Expected Impact: {pattern.get('metrics', 'N/A')}
"""
    
    enhanced_prompt = base_prompt + rag_context + "\n\n📸 Now analyze the uploaded design image considering these patterns and best practices."
    
    return enhanced_prompt