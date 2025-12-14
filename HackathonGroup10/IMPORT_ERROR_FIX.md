# ✅ Import Error Fixed!

## 🐛 Error
```
NameError: name 'Document' is not defined
```

## 🔧 Root Cause
The `Document` class from `langchain.schema` was only imported when RAG dependencies were available. However, the type hint `doc: Document` in the `_calculate_relevance` method is evaluated at class definition time, which happens before the try/except can handle the import error.

## ✅ Fix Applied
Added a fallback `Document` class in the `except ImportError` block so that `Document` is always defined, even when RAG dependencies are not installed.

### Before:
```python
try:
    from langchain.schema import Document
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    # Document not defined here!
```

### After:
```python
try:
    from langchain.schema import Document
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    # Create a dummy Document class for type hints when RAG is not available
    class Document:
        def __init__(self, page_content: str = "", metadata: Dict = None):
            self.page_content = page_content
            self.metadata = metadata or {}
```

## ✅ Verification
- ✅ `CVERAGAgent` imports successfully
- ✅ Agent can be instantiated
- ✅ No import errors

## 📁 Files Fixed
- `deploy_hf/agents/cve_rag_agent.py`
- `agents/cve_rag_agent.py` (source file)

---

**The error is now fixed!** The app should start successfully on Hugging Face Spaces. 🚀
