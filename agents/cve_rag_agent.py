"""
CVE RAG Agent - Retrieves and correlates CVE information using RAG
Uses vector database to search and retrieve relevant CVE details
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import re

from .base_agent import BaseAgent, SecurityAlert, AlertSeverity

try:
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    # Create a dummy Document class for type hints when RAG is not available
    class Document:
        def __init__(self, page_content: str = "", metadata: Dict = None):
            self.page_content = page_content
            self.metadata = metadata or {}
    # No warning - falls back gracefully to simple search


class CVERAGAgent(BaseAgent):
    """RAG-powered CVE and vulnerability intelligence agent"""
    
    # CVE database (in production, this would be from NVD API or other sources)
    CVE_DATABASE = {
        "CVE-2024-0001": {
            "id": "CVE-2024-0001",
            "description": "Remote code execution vulnerability in Apache web server versions before 2.4.58",
            "severity": "CRITICAL",
            "cvss_score": 9.8,
            "affected_versions": ["<2.4.58"],
            "published_date": "2024-01-15",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-0001"]
        },
        "CVE-2024-0002": {
            "id": "CVE-2024-0002",
            "description": "Privilege escalation vulnerability in MySQL database versions before 8.0.35",
            "severity": "HIGH",
            "cvss_score": 7.5,
            "affected_versions": ["<8.0.35"],
            "published_date": "2024-01-20",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-0002"]
        },
        "CVE-2024-0003": {
            "id": "CVE-2024-0003",
            "description": "SQL injection vulnerability in Django framework versions 3.2.x and 4.0.x",
            "severity": "HIGH",
            "cvss_score": 8.1,
            "affected_versions": ["<3.2.24", "<4.0.10"],
            "published_date": "2024-02-01",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-0003"]
        }
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("cve_rag", "CVE RAG Agent", config)
        self.vector_store = None
        self.embeddings = None
        self._initialize_rag_system()
    
    def _initialize_rag_system(self) -> None:
        """Initialize RAG system with CVE database"""
        if not RAG_AVAILABLE:
            # Falls back to keyword search - no warning needed
            return
        
        try:
            # Initialize embeddings (using lightweight model)
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            # Convert CVE database to documents
            documents = []
            for cve_id, cve_data in self.CVE_DATABASE.items():
                # Create rich text representation for better retrieval
                text = f"""
                CVE ID: {cve_id}
                Description: {cve_data['description']}
                Severity: {cve_data['severity']}
                CVSS Score: {cve_data['cvss_score']}
                Affected Versions: {', '.join(cve_data['affected_versions'])}
                Published: {cve_data['published_date']}
                References: {', '.join(cve_data['references'])}
                """
                
                doc = Document(
                    page_content=text.strip(),
                    metadata={
                        "cve_id": cve_id,
                        "severity": cve_data["severity"],
                        "cvss_score": cve_data["cvss_score"],
                        "published_date": cve_data["published_date"]
                    }
                )
                documents.append(doc)
            
            # Create vector store
            if documents:
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
                self.logger.info(f"Initialized RAG system with {len(documents)} CVEs")
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG system: {e}")
            self.vector_store = None
    
    def search_cves(self, query: str, software_name: Optional[str] = None, 
                   version: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant CVEs using RAG"""
        results = []
        
        # Build search query
        search_query = query
        if software_name:
            search_query = f"{software_name} {version} {query}" if version else f"{software_name} {query}"
        
        # Use RAG if available
        if self.vector_store and RAG_AVAILABLE:
            try:
                # Semantic search
                docs = self.vector_store.similarity_search(search_query, k=limit)
                
                for doc in docs:
                    cve_id = doc.metadata.get("cve_id")
                    if cve_id and cve_id in self.CVE_DATABASE:
                        cve_data = self.CVE_DATABASE[cve_id].copy()
                        cve_data["relevance_score"] = self._calculate_relevance(doc, software_name, version)
                        results.append(cve_data)
            except Exception as e:
                self.logger.error(f"RAG search failed: {e}")
                # Fallback to keyword search
                results = self._keyword_search(search_query, software_name, version, limit)
        else:
            # Fallback to keyword search
            results = self._keyword_search(search_query, software_name, version, limit)
        
        return results
    
    def _keyword_search(self, query: str, software_name: Optional[str] = None,
                       version: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Fallback keyword-based search"""
        results = []
        query_lower = query.lower()
        
        for cve_id, cve_data in self.CVE_DATABASE.items():
            # Check if query matches
            if (query_lower in cve_data["description"].lower() or
                (software_name and software_name.lower() in cve_data["description"].lower())):
                
                cve_result = cve_data.copy()
                cve_result["relevance_score"] = 0.7  # Default relevance
                results.append(cve_result)
        
        # Sort by severity and limit
        results.sort(key=lambda x: (x["cvss_score"], x["severity"]), reverse=True)
        return results[:limit]
    
    def _calculate_relevance(self, doc: Document, software_name: Optional[str] = None,
                            version: Optional[str] = None) -> float:
        """Calculate relevance score for CVE match"""
        score = 0.5  # Base score
        
        # Check software name match
        if software_name and software_name.lower() in doc.page_content.lower():
            score += 0.3
        
        # Check version match
        if version:
            # Check if version is in affected versions
            for affected in doc.metadata.get("affected_versions", []):
                if self._version_matches(version, affected):
                    score += 0.2
                    break
        
        return min(score, 1.0)
    
    def _version_matches(self, version: str, affected_pattern: str) -> bool:
        """Check if version matches affected pattern"""
        # Simple version comparison (e.g., "2.0.0" matches "<2.4.58")
        if affected_pattern.startswith("<"):
            try:
                threshold = affected_pattern[1:]
                return self._compare_versions(version, threshold) < 0
            except:
                return False
        return False
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare version strings"""
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            v1_val = v1_parts[i] if i < len(v1_parts) else 0
            v2_val = v2_parts[i] if i < len(v2_parts) else 0
            
            if v1_val < v2_val:
                return -1
            elif v1_val > v2_val:
                return 1
        return 0
    
    def get_cve_details(self, cve_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed CVE information"""
        return self.CVE_DATABASE.get(cve_id)
    
    def check_software_vulnerability(self, software_name: str, version: str) -> List[SecurityAlert]:
        """Check if software version has known vulnerabilities"""
        alerts = []
        
        # Search for relevant CVEs
        cves = self.search_cves(
            query=f"{software_name} vulnerability",
            software_name=software_name,
            version=version,
            limit=10
        )
        
        for cve in cves:
            # Check if version is affected
            is_affected = False
            for affected_version in cve.get("affected_versions", []):
                if self._version_matches(version, affected_version):
                    is_affected = True
                    break
            
            if is_affected:
                severity_map = {
                    "CRITICAL": AlertSeverity.CRITICAL,
                    "HIGH": AlertSeverity.HIGH,
                    "MEDIUM": AlertSeverity.MEDIUM,
                    "LOW": AlertSeverity.LOW
                }
                
                alert = SecurityAlert(
                    agent_id=self.agent_id,
                    alert_type="cve_vulnerability",
                    severity=severity_map.get(cve["severity"], AlertSeverity.MEDIUM),
                    description=f"{software_name} {version} is vulnerable to {cve['id']}: {cve['description']}",
                    details={
                        "cve_id": cve["id"],
                        "software": software_name,
                        "version": version,
                        "cvss_score": cve["cvss_score"],
                        "severity": cve["severity"],
                        "published_date": cve["published_date"],
                        "references": cve.get("references", []),
                        "relevance_score": cve.get("relevance_score", 0.0)
                    }
                )
                alerts.append(alert)
        
        # Send alerts
        for alert in alerts:
            self.send_alert(alert)
        
        return alerts
    
    def search_unknown_vulnerabilities(self, query: str, context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for vulnerabilities using natural language query"""
        # Use RAG to find relevant vulnerabilities
        results = self.search_cves(query, limit=10)
        
        # Enhance with context if provided
        if context:
            software_name = context.get("software_name")
            version = context.get("version")
            if software_name:
                results = self.search_cves(
                    query,
                    software_name=software_name,
                    version=version,
                    limit=10
                )
        
        return results
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "rag_enabled": self.vector_store is not None,
            "cve_database_size": len(self.CVE_DATABASE),
            "search_methods": ["semantic_search", "keyword_search"],
            "features": [
                "cve_search",
                "software_vulnerability_check",
                "natural_language_query",
                "version_matching",
                "relevance_scoring"
            ]
        }
    
    def analyze(self, data: Any) -> List[SecurityAlert]:
        """Analyze data for vulnerabilities"""
        if isinstance(data, dict):
            software_name = data.get("software_name") or data.get("name")
            version = data.get("version")
            
            if software_name and version:
                return self.check_software_vulnerability(software_name, version)
            elif "query" in data:
                # Natural language query
                results = self.search_unknown_vulnerabilities(
                    data["query"],
                    data.get("context")
                )
                # Convert to alerts if needed
                return []
        elif isinstance(data, str):
            # Natural language query
            results = self.search_unknown_vulnerabilities(data)
            return []
        
        return []
    
    def add_cve_to_database(self, cve_data: Dict[str, Any]) -> None:
        """Add new CVE to database (for dynamic updates)"""
        cve_id = cve_data.get("id")
        if cve_id:
            self.CVE_DATABASE[cve_id] = cve_data
            # Rebuild vector store if RAG is enabled
            if RAG_AVAILABLE:
                self._initialize_rag_system()
            self.logger.info(f"Added CVE {cve_id} to database")
    
    def update_from_external_source(self, cve_list: List[Dict[str, Any]]) -> None:
        """Update CVE database from external source (e.g., NVD API)"""
        for cve_data in cve_list:
            self.add_cve_to_database(cve_data)
        self.logger.info(f"Updated database with {len(cve_list)} CVEs")
