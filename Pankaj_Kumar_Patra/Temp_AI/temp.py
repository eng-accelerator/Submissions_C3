import os
import re
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple, Any
import urllib3
from dotenv import load_dotenv
from jira import JIRA

# LangChain + Vector DB
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# -------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------
load_dotenv()

# Jira Configuration
JIRA_URL = os.getenv("JIRA_URL", "https://your-jira-instance.atlassian.net")
JIRA_USER = os.getenv("JIRA_USER", "")
JIRA_TOKEN = os.getenv("JIRA_TOKEN", "")
JIRA_PROJECT = os.getenv("JIRA_PROJECT", "PROJ")
VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() == "true"

# LLM Configuration (OpenAI or OpenRouter)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "anthropic/claude-3.5-sonnet")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")  # For OpenRouter or custom endpoints

# Embedding Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# RAG Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))

# Data persistence
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./faiss_index")
SYNC_STATE_PATH = os.getenv("SYNC_STATE_PATH", "./sync_state.json")
DEFAULT_SINCE_DAYS = int(os.getenv("DEFAULT_SINCE_DAYS", "180"))

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
log = logging.getLogger("jira-rag-agent")

if not VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print(f"🔧 Configuration Loaded:")
print(f"  JIRA: {JIRA_URL} | Project: {JIRA_PROJECT}")
print(f"  LLM: {LLM_MODEL}")
print(f"  Embeddings: {EMBEDDING_MODEL}")
print(f"  Vector Store: {VECTOR_STORE_PATH}")

# -------------------------------------------------------------------------
# Jira Client
# -------------------------------------------------------------------------
class JiraClient:
    """Handles all Jira API interactions"""
    
    def __init__(self):
        if not JIRA_URL or not JIRA_USER or not JIRA_TOKEN:
            raise ValueError("Missing Jira credentials. Check JIRA_URL, JIRA_USER, JIRA_TOKEN")
        
        self.jira = JIRA(
            options={"server": JIRA_URL, "verify": VERIFY_SSL},
            basic_auth=(JIRA_USER, JIRA_TOKEN)
        )
        log.info(f"✅ Connected to Jira: {JIRA_URL}")
    
    def fetch_issues(
        self, 
        project: str = JIRA_PROJECT,
        since_days: Optional[int] = None,
        jql_filter: Optional[str] = None,
        max_results: int = 1000
    ) -> List[Document]:
        """Fetch Jira issues and convert to LangChain Documents"""
        
        # Build JQL query
        if jql_filter:
            jql = jql_filter
        elif since_days:
            jql = f'project = {project} AND updated >= -{since_days}d ORDER BY updated DESC'
        else:
            jql = f'project = {project} ORDER BY updated DESC'
        
        log.info(f"🔍 Executing JQL: {jql}")
        
        documents = []
        start_at = 0
        batch_size = 100
        
        while start_at < max_results:
            issues = self.jira.search_issues(
                jql,
                startAt=start_at,
                maxResults=min(batch_size, max_results - start_at),
                fields="summary,status,description,comment,created,updated,priority,assignee,reporter,issuetype"
            )
            
            if not issues:
                break
            
            for issue in issues:
                doc = self._issue_to_document(issue)
                documents.append(doc)
            
            start_at += len(issues)
            log.info(f"  Fetched {start_at} issues...")
        
        log.info(f"✅ Total issues fetched: {len(documents)}")
        return documents
    
    def fetch_single_issue(self, issue_key: str) -> Optional[Document]:
        """Fetch a single issue by key"""
        try:
            issue = self.jira.issue(
                issue_key,
                fields="summary,status,description,comment,created,updated,priority,assignee,reporter,issuetype"
            )
            return self._issue_to_document(issue)
        except Exception as e:
            log.error(f"❌ Failed to fetch {issue_key}: {e}")
            return None
    
    def search_by_error(self, error_text: str, max_results: int = 20) -> List[Document]:
        """Search Jira for issues containing specific error text"""
        # Escape special JQL characters
        escaped_error = error_text.replace('"', '\\"')
        jql = f'project = {JIRA_PROJECT} AND text ~ "{escaped_error}" ORDER BY updated DESC'
        
        log.info(f"🔎 Searching for error: {error_text[:100]}...")
        
        try:
            issues = self.jira.search_issues(
                jql,
                maxResults=max_results,
                fields="summary,status,description,comment,created,updated,priority"
            )
            return [self._issue_to_document(issue) for issue in issues]
        except Exception as e:
            log.error(f"❌ Error search failed: {e}")
            return []
    
    def _issue_to_document(self, issue) -> Document:
        """Convert Jira issue to LangChain Document"""
        fields = issue.fields
        
        # Extract comments
        comments_text = ""
        try:
            if hasattr(fields.comment, 'comments'):
                comments = []
                for comment in fields.comment.comments:
                    author = getattr(comment.author, 'displayName', 'Unknown')
                    body = getattr(comment, 'body', '')
                    created = getattr(comment, 'created', '')
                    comments.append(f"[{author} | {created}]\n{body}")
                comments_text = "\n\n".join(comments)
        except:
            comments_text = "No comments available"
        
        # Build content
        content = f"""Ticket ID: {issue.key}
Summary: {getattr(fields, 'summary', 'N/A')}
Status: {getattr(fields.status, 'name', 'Unknown')}
Priority: {getattr(getattr(fields, 'priority', None), 'name', 'N/A')}
Type: {getattr(getattr(fields, 'issuetype', None), 'name', 'N/A')}
Assignee: {getattr(getattr(fields, 'assignee', None), 'displayName', 'Unassigned')}
Reporter: {getattr(getattr(fields, 'reporter', None), 'displayName', 'Unknown')}
Created: {getattr(fields, 'created', 'N/A')[:10]}
Updated: {getattr(fields, 'updated', 'N/A')[:10]}

Description:
{getattr(fields, 'description', 'No description')}

Comments:
{comments_text}
"""
        
        # Metadata
        metadata = {
            "source": issue.key,
            "project": JIRA_PROJECT,
            "summary": getattr(fields, 'summary', ''),
            "status": getattr(fields.status, 'name', 'Unknown'),
            "priority": getattr(getattr(fields, 'priority', None), 'name', 'N/A'),
            "created": getattr(fields, 'created', '')[:10],
            "updated": getattr(fields, 'updated', '')[:10],
            "url": f"{JIRA_URL}/browse/{issue.key}"
        }
        
        return Document(page_content=content, metadata=metadata)

# -------------------------------------------------------------------------
# Vector Store Manager
# -------------------------------------------------------------------------
class VectorStoreManager:
    """Manages vector store creation and persistence"""
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
    
    def create_or_load_vector_store(self, documents: List[Document]) -> FAISS:
        """Create new vector store or load existing one"""
        
        # Try loading existing store
        if os.path.exists(VECTOR_STORE_PATH):
            try:
                log.info(f"📂 Loading existing vector store from {VECTOR_STORE_PATH}")
                self.vector_store = FAISS.load_local(
                    VECTOR_STORE_PATH,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                log.info("✅ Vector store loaded successfully")
                return self.vector_store
            except Exception as e:
                log.warning(f"⚠️ Failed to load existing store: {e}. Creating new one...")
        
        # Create new store
        log.info("🔨 Creating new vector store...")
        chunks = self.text_splitter.split_documents(documents)
        log.info(f"  Split into {len(chunks)} chunks")
        
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        self.save_vector_store()
        
        return self.vector_store
    
    def add_documents(self, documents: List[Document]):
        """Add new documents to existing vector store"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        chunks = self.text_splitter.split_documents(documents)
        log.info(f"➕ Adding {len(chunks)} new chunks to vector store")
        self.vector_store.add_documents(chunks)
        self.save_vector_store()
    
    def save_vector_store(self):
        """Persist vector store to disk"""
        if self.vector_store:
            os.makedirs(os.path.dirname(VECTOR_STORE_PATH) or ".", exist_ok=True)
            self.vector_store.save_local(VECTOR_STORE_PATH)
            log.info(f"💾 Vector store saved to {VECTOR_STORE_PATH}")

# -------------------------------------------------------------------------
# Jira RAG Agent
# -------------------------------------------------------------------------
class JiraRAGAgent:
    """Main RAG agent for Jira queries"""
    
    def __init__(self):
        self.jira_client = JiraClient()
        self.vector_manager = VectorStoreManager()
        
        # Initialize LLM (supports OpenAI, OpenRouter, or compatible APIs)
        api_key = OPENROUTER_API_KEY or OPENAI_API_KEY
        if not api_key:
            raise ValueError("Missing API key. Set OPENROUTER_API_KEY or OPENAI_API_KEY")
        
        llm_kwargs = {
            "model": LLM_MODEL,
            "temperature": 0,
            "openai_api_key": api_key
        }
        
        # Add custom base URL if specified (for OpenRouter or other providers)
        if LLM_BASE_URL:
            llm_kwargs["openai_api_base"] = LLM_BASE_URL
        elif OPENROUTER_API_KEY:
            llm_kwargs["openai_api_base"] = "https://openrouter.ai/api/v1"
        
        self.llm = ChatOpenAI(**llm_kwargs)
        self.issue_key_pattern = re.compile(r'\b([A-Z][A-Z0-9]+-\d+)\b')
        
        # Custom prompt template
        self.prompt_template = PromptTemplate(
            template="""You are a helpful Jira assistant. Use the following Jira ticket information to answer the question.
If you don't know the answer based on the provided context, say so clearly.

Context from Jira tickets:
{context}

Question: {question}

Provide a detailed answer that:
1. Directly addresses the question
2. References specific ticket IDs when relevant
3. Includes relevant technical details from the tickets
4. Mentions current status and any solutions or workarounds found
5. Quotes exact error messages or key information when helpful

Answer:""",
            input_variables=["context", "question"]
        )
    
    def initialize(self, force_refresh: bool = False):
        """Initialize or refresh the knowledge base"""
        log.info("🚀 Initializing Jira RAG Agent...")
        
        if force_refresh or not os.path.exists(VECTOR_STORE_PATH):
            # Full refresh
            documents = self.jira_client.fetch_issues(since_days=DEFAULT_SINCE_DAYS)
            self.vector_manager.create_or_load_vector_store(documents)
            self._save_sync_state(documents)
        else:
            # Load existing and do incremental update
            self.vector_manager.create_or_load_vector_store([])
            self._incremental_update()
        
        log.info("✅ Agent initialization complete")
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Main query interface. Handles:
        - Direct ticket ID queries (e.g., "PROJ-123")
        - Error message searches
        - Natural language questions
        """
        
        question = question.strip()
        
        # Check if it's a direct ticket ID
        if self.issue_key_pattern.fullmatch(question.upper()):
            return self._handle_ticket_query(question.upper())
        
        # Check if it looks like an error message
        if self._is_error_message(question):
            return self._handle_error_query(question)
        
        # Handle as natural language query
        return self._handle_nlq(question)
    
    def _handle_ticket_query(self, ticket_id: str) -> Dict[str, Any]:
        """Handle direct ticket ID queries"""
        log.info(f"🎫 Fetching ticket: {ticket_id}")
        
        doc = self.jira_client.fetch_single_issue(ticket_id)
        if not doc:
            return {
                "answer": f"❌ Ticket {ticket_id} not found or inaccessible.",
                "sources": [],
                "query_type": "ticket_id"
            }
        
        # Generate detailed analysis
        prompt = f"""Analyze this Jira ticket and provide a comprehensive summary:

{doc.page_content}

Provide:
1. Brief summary of the issue
2. Current status
3. Root cause (if mentioned)
4. Solution or workaround (if any)
5. Key insights from comments
"""
        
        response = self.llm.invoke(prompt)
        
        return {
            "answer": f"### 🎫 {ticket_id}\n\n{response.content}",
            "sources": [doc],
            "query_type": "ticket_id",
            "ticket_url": doc.metadata.get("url")
        }
    
    def _handle_error_query(self, error_text: str) -> Dict[str, Any]:
        """Handle error message searches"""
        log.info(f"🔍 Searching for error: {error_text[:100]}...")
        
        # Search Jira directly for this error
        jira_docs = self.jira_client.search_by_error(error_text, max_results=10)
        
        # Also search vector store
        if self.vector_manager.vector_store:
            vector_docs = self.vector_manager.vector_store.similarity_search(
                error_text, k=TOP_K_RESULTS
            )
        else:
            vector_docs = []
        
        # Combine and deduplicate
        all_docs = self._deduplicate_docs(jira_docs + vector_docs)
        
        if not all_docs:
            return {
                "answer": "❌ No Jira tickets found containing this error message.",
                "sources": [],
                "query_type": "error_search"
            }
        
        # Generate answer using RAG
        context = "\n\n---\n\n".join([doc.page_content for doc in all_docs[:TOP_K_RESULTS]])
        prompt = self.prompt_template.format(context=context, question=f"What issues are related to this error: {error_text}")
        
        response = self.llm.invoke(prompt)
        
        return {
            "answer": response.content,
            "sources": all_docs[:TOP_K_RESULTS],
            "query_type": "error_search",
            "total_matches": len(all_docs)
        }
    
    def _handle_nlq(self, question: str) -> Dict[str, Any]:
        """Handle natural language questions using RAG"""
        log.info(f"💬 Processing NLQ: {question}")
        
        if not self.vector_manager.vector_store:
            return {
                "answer": "❌ Vector store not initialized. Please run initialize() first.",
                "sources": [],
                "query_type": "nlq"
            }
        
        # Retrieve relevant documents
        docs = self.vector_manager.vector_store.similarity_search_with_score(
            question, k=TOP_K_RESULTS * 2
        )
        
        # Filter by similarity threshold
        relevant_docs = [doc for doc, score in docs if score >= SIMILARITY_THRESHOLD]
        
        if not relevant_docs:
            return {
                "answer": "❌ No relevant tickets found for this query. Try rephrasing or checking if the information exists in Jira.",
                "sources": [],
                "query_type": "nlq"
            }
        
        # Generate answer
        context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs[:TOP_K_RESULTS]])
        prompt = self.prompt_template.format(context=context, question=question)
        
        response = self.llm.invoke(prompt)
        
        return {
            "answer": response.content,
            "sources": relevant_docs[:TOP_K_RESULTS],
            "query_type": "nlq"
        }
    
    def _is_error_message(self, text: str) -> bool:
        """Heuristic to detect if text is an error message"""
        error_indicators = [
            'error', 'exception', 'failed', 'failure', 'traceback',
            'stackoverflow', 'nullpointerexception', 'timeout',
            'connection refused', 'cannot', 'unable to'
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in error_indicators) or len(text) > 100
    
    def _deduplicate_docs(self, docs: List[Document]) -> List[Document]:
        """Remove duplicate documents based on source key"""
        seen = set()
        unique = []
        for doc in docs:
            key = doc.metadata.get("source")
            if key and key not in seen:
                seen.add(key)
                unique.append(doc)
        return unique
    
    def _incremental_update(self):
        """Fetch and add only new/updated tickets"""
        state = self._load_sync_state()
        last_sync = state.get("last_sync_date")
        
        if last_sync:
            # Calculate days since last sync
            try:
                last_date = datetime.fromisoformat(last_sync)
                days_ago = (datetime.now() - last_date).days + 1
            except:
                days_ago = 7  # Default fallback
        else:
            days_ago = 7
        
        log.info(f"🔄 Incremental update: fetching tickets from last {days_ago} days")
        new_docs = self.jira_client.fetch_issues(since_days=days_ago)
        
        if new_docs:
            self.vector_manager.add_documents(new_docs)
            self._save_sync_state(new_docs)
    
    def _load_sync_state(self) -> dict:
        """Load sync state from file"""
        try:
            with open(SYNC_STATE_PATH, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_sync_state(self, docs: List[Document]):
        """Save sync state to file"""
        state = {
            "last_sync_date": datetime.now().isoformat(),
            "total_documents": len(docs),
            "latest_ticket": docs[0].metadata.get("source") if docs else None
        }
        
        with open(SYNC_STATE_PATH, 'w') as f:
            json.dump(state, f, indent=2)

# -------------------------------------------------------------------------
# CLI Interface
# -------------------------------------------------------------------------
def main():
    """Interactive CLI for the Jira RAG Agent"""
    print("=" * 70)
    print("🤖 JIRA RAG AGENT")
    print("=" * 70)
    
    # Initialize agent
    agent = JiraRAGAgent()
    
    print("\nInitializing knowledge base...")
    print("(Use --refresh flag to force full refresh)")
    
    import sys
    force_refresh = "--refresh" in sys.argv
    agent.initialize(force_refresh=force_refresh)
    
    print("\n" + "=" * 70)
    print("Ready! Ask me about Jira tickets, errors, or general questions.")
    print("Examples:")
    print("  - PROJ-123")
    print("  - NullPointerException in authentication module")
    print("  - What are the recent login issues?")
    print("\nType 'exit' to quit.")
    print("=" * 70)
    
    while True:
        try:
            question = input("\n🧑 You: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            # Process query
            print("\n🤖 Agent: Searching...\n")
            result = agent.query(question)
            
            # Display answer
            print(result["answer"])
            
            # Display sources
            if result["sources"]:
                print(f"\n📚 Sources ({len(result['sources'])} tickets):")
                for doc in result["sources"]:
                    meta = doc.metadata
                    print(f"  • {meta.get('source')} - {meta.get('summary', 'N/A')[:60]}... [{meta.get('status')}]")
                    if 'url' in meta:
                        print(f"    {meta['url']}")
            
            print("\n" + "-" * 70)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            log.error(f"Error processing query: {e}")
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
