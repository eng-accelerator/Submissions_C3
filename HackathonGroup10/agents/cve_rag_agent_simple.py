"""
CVE RAG Agent - Simple Version (No FAISS Required)
Uses simple dictionary search - no external dependencies
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from .base_agent import BaseAgent, SecurityAlert, AlertSeverity


class CVERAGAgentSimple(BaseAgent):
    """Simple CVE RAG Agent - No external dependencies"""
    
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
        super().__init__("cve_rag", "CVE RAG Agent (Simple)", config)
    
    def search_cves(self, query: str, software_name: Optional[str] = None, 
                   version: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant CVEs using keyword matching"""
        results = []
        query_lower = query.lower()
        
        # Build search terms
        search_terms = [query_lower]
        if software_name:
            search_terms.append(software_name.lower())
        if version:
            search_terms.append(version.lower())
        
        # Search through CVE database
        for cve_id, cve_data in self.CVE_DATABASE.items():
            score = 0.0
            description_lower = cve_data["description"].lower()
            
            # Check if any search term matches
            for term in search_terms:
                if term in description_lower:
                    score += 0.3
                if term in cve_id.lower():
                    score += 0.2
            
            # Check software name match
            if software_name and software_name.lower() in description_lower:
                score += 0.3
            
            # Check version match
            if version:
                for affected_version in cve_data.get("affected_versions", []):
                    if self._version_matches(version, affected_version):
                        score += 0.2
                        break
            
            if score > 0:
                cve_result = cve_data.copy()
                cve_result["relevance_score"] = min(score, 1.0)
                results.append(cve_result)
        
        # Sort by relevance and severity
        results.sort(key=lambda x: (x["relevance_score"], x["cvss_score"]), reverse=True)
        return results[:limit]
    
    def _version_matches(self, version: str, affected_pattern: str) -> bool:
        """Check if version matches affected pattern"""
        if affected_pattern.startswith("<"):
            try:
                threshold = affected_pattern[1:]
                return self._compare_versions(version, threshold) < 0
            except:
                return False
        return False
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare version strings"""
        try:
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
        except:
            return 0
    
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
        software_name = context.get("software_name") if context else None
        version = context.get("version") if context else None
        
        results = self.search_cves(query, software_name, version, limit=10)
        return results
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "rag_enabled": False,  # Simple version, no vector DB
            "cve_database_size": len(self.CVE_DATABASE),
            "search_methods": ["keyword_search"],
            "features": [
                "cve_search",
                "software_vulnerability_check",
                "keyword_query",
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
                self.search_unknown_vulnerabilities(data["query"], data.get("context"))
                return []
        elif isinstance(data, str):
            self.search_unknown_vulnerabilities(data)
            return []
        
        return []
    
    def add_cve_to_database(self, cve_data: Dict[str, Any]) -> None:
        """Add new CVE to database"""
        cve_id = cve_data.get("id")
        if cve_id:
            self.CVE_DATABASE[cve_id] = cve_data
            self.logger.info(f"Added CVE {cve_id} to database")
    
    def update_from_external_source(self, cve_list: List[Dict[str, Any]]) -> None:
        """Update CVE database from external source"""
        for cve_data in cve_list:
            self.add_cve_to_database(cve_data)
        self.logger.info(f"Updated database with {len(cve_list)} CVEs")
