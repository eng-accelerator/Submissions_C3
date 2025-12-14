from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
import os

def create_vector_store(file_path: str, api_key: str = None):
    """
    Ingests a file and creates a temporary vector store using local embeddings.
    """
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)
        
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    
    # Use local embeddings to avoid API key issues involved with OpenRouter/OpenAI
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(splits, embeddings)
    return vectorstore

def cookbook_agent(state: dict, api_key: str, vector_store):
    """
    Retrieves relevant cookbook entries based on log analysis.
    """
    analysis = state.get("analysis_results", "")
    if not analysis:
         return {"errors": ["No log analysis found to query cookbook."]}
         
    # Assuming analysis is text or JSON string, we use it as query
    query = f"Find remediation steps for: {str(analysis)}"
    
    docs = vector_store.similarity_search(query, k=3)
    
    # Format context with page numbers for citation
    context_parts = []
    for d in docs:
        # Pypdfloader uses 0-indexed 'page' in metadata
        page_num = d.metadata.get('page', 'N/A')
        # Add 1 if it's a number to make it human-readable (1-indexed)
        if isinstance(page_num, int):
            page_num += 1
        
        context_parts.append(f"[Source: Cookbook, Page: {page_num}]\n{d.page_content}")
    
    context = "\n\n".join(context_parts)
    
    return {"cookbook_context": context}
