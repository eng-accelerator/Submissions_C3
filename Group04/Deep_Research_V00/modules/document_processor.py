import io
from typing import List, Dict, Any
import pypdf
import docx

class DocumentProcessor:
    """
    Handles extracting text from various document formats (PDF, DOCX).
    """

    @staticmethod
    def process_pdf(file_bytes: bytes, filename: str) -> str:
        """
        Extract text from a PDF file.
        """
        try:
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF {filename}: {str(e)}"

    @staticmethod
    def process_docx(file_bytes: bytes, filename: str) -> str:
        """
        Extract text from a DOCX file.
        """
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            return f"Error reading DOCX {filename}: {str(e)}"

    @staticmethod
    def process_uploaded_files(uploaded_files: List[Any]) -> List[Dict[str, str]]:
        """
        Process a list of Streamlit uploaded files.
        """
        documents = []
        for uploaded_file in uploaded_files:
            file_type = uploaded_file.name.split('.')[-1].lower()
            content = ""
            
            if file_type == 'pdf':
                content = DocumentProcessor.process_pdf(uploaded_file.getvalue(), uploaded_file.name)
            elif file_type in ['docx', 'doc']:
                content = DocumentProcessor.process_docx(uploaded_file.getvalue(), uploaded_file.name)
            else:
                content = f"Unsupported file type: {file_type}"
            
            documents.append({
                "source": uploaded_file.name,
                "content": content,
                "type": "user_upload"
            })
        return documents
