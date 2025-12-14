from typing import List, Dict, Any
import re
import tiktoken

# Updated import for newer LangChain versions
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
except ImportError:
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
    except ImportError:
        # Fallback: create a simple text splitter if langchain not available
        class RecursiveCharacterTextSplitter:
            def __init__(self, chunk_size=1000, chunk_overlap=200, length_function=len, separators=None):
                self.chunk_size = chunk_size
                self.chunk_overlap = chunk_overlap
                self.length_function = length_function
                self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
            
            def split_text(self, text: str) -> List[str]:
                """Simple fallback text splitter"""
                chunks = []
                current_chunk = ""
                
                for char in text:
                    current_chunk += char
                    if len(current_chunk) >= self.chunk_size:
                        chunks.append(current_chunk)
                        # Keep overlap
                        current_chunk = current_chunk[-self.chunk_overlap:] if self.chunk_overlap > 0 else ""
                
                if current_chunk:
                    chunks.append(current_chunk)
                
                return chunks

class TextChunker:
    """Split text into chunks for embedding and retrieval"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            print(f"Warning: Could not load tiktoken encoding: {e}")
            self.encoding = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except:
                pass
        # Fallback: estimate tokens as ~4 chars per token
        return len(text) // 4
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Split text into chunks with metadata"""
        if not text or not text.strip():
            return []
        
        # Create text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Split text
        chunks = text_splitter.split_text(text)
        
        # Create chunk objects with metadata
        chunk_objects = []
        for i, chunk in enumerate(chunks):
            chunk_obj = {
                'chunk_id': i,
                'text': chunk,
                'token_count': self.count_tokens(chunk),
                'char_count': len(chunk),
                'metadata': metadata or {}
            }
            chunk_objects.append(chunk_obj)
        
        return chunk_objects
    
    def chunk_document(self, processed_doc: Dict[str, Any], doc_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Chunk a processed document"""
        if not processed_doc.get('success'):
            return []
        
        full_text = processed_doc.get('full_text', '')
        file_type = processed_doc.get('file_type', 'unknown')
        
        # Base metadata
        base_metadata = doc_metadata or {}
        base_metadata['file_type'] = file_type
        base_metadata['source'] = base_metadata.get('file_name', 'unknown')
        
        # For PDFs with page information
        if file_type == 'pdf' and 'text_content' in processed_doc:
            all_chunks = []
            for page_data in processed_doc['text_content']:
                page_num = page_data.get('page', 0)
                page_text = page_data.get('content', '')
                
                page_metadata = base_metadata.copy()
                page_metadata['page'] = page_num
                
                chunks = self.chunk_text(page_text, page_metadata)
                all_chunks.extend(chunks)
            
            return all_chunks
        
        # For other file types, chunk the full text
        return self.chunk_text(full_text, base_metadata)
    
    def chunk_structured_data(self, data: List[Dict[str, Any]], metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Convert structured data (like Excel rows) into text chunks"""
        chunks = []
        
        for i, record in enumerate(data):
            # Convert record to text
            text_parts = []
            for key, value in record.items():
                text_parts.append(f"{key}: {value}")
            
            record_text = "\n".join(text_parts)
            
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata['record_index'] = i
            chunk_metadata['data_type'] = 'structured'
            
            chunk_obj = {
                'chunk_id': i,
                'text': record_text,
                'token_count': self.count_tokens(record_text),
                'char_count': len(record_text),
                'metadata': chunk_metadata,
                'structured_data': record
            }
            chunks.append(chunk_obj)
        
        return chunks
    
    def merge_small_chunks(self, chunks: List[Dict[str, Any]], min_size: int = 100) -> List[Dict[str, Any]]:
        """Merge chunks that are too small"""
        if not chunks:
            return []
        
        merged_chunks = []
        current_chunk = None
        
        for chunk in chunks:
            if current_chunk is None:
                current_chunk = chunk.copy()
            elif chunk['char_count'] < min_size:
                # Merge with current chunk
                current_chunk['text'] += '\n\n' + chunk['text']
                current_chunk['char_count'] += chunk['char_count']
                current_chunk['token_count'] += chunk['token_count']
            else:
                # Save current chunk and start new one
                merged_chunks.append(current_chunk)
                current_chunk = chunk.copy()
        
        # Add last chunk
        if current_chunk:
            merged_chunks.append(current_chunk)
        
        # Reindex chunks
        for i, chunk in enumerate(merged_chunks):
            chunk['chunk_id'] = i
        
        return merged_chunks
    
    def create_summary_chunk(self, chunks: List[Dict[str, Any]], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a summary chunk from multiple chunks"""
        if not chunks:
            return None
        
        # Combine first and last chunks for context
        first_chunk = chunks[0]['text'][:500] if len(chunks[0]['text']) > 500 else chunks[0]['text']
        last_chunk = chunks[-1]['text'][-500:] if len(chunks[-1]['text']) > 500 else chunks[-1]['text']
        
        summary_text = f"Document Summary:\n\nBeginning:\n{first_chunk}\n\n...\n\nEnding:\n{last_chunk}"
        
        summary_metadata = metadata.copy() if metadata else {}
        summary_metadata['chunk_type'] = 'summary'
        summary_metadata['num_chunks'] = len(chunks)
        
        return {
            'chunk_id': -1,
            'text': summary_text,
            'token_count': self.count_tokens(summary_text),
            'char_count': len(summary_text),
            'metadata': summary_metadata
        }