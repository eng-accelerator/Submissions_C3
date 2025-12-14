"""
External API Agent - Connects to external data sources WITHOUT RAG
Uses direct HTTP API calls to fetch real-time threat intelligence and CVE data
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import requests
from .base_agent import BaseAgent, SecurityAlert, AlertSeverity


class ExternalAPIAgent(BaseAgent):
    """
    Agent that connects to external APIs for threat intelligence and CVE data
    Works WITHOUT RAG - uses direct HTTP API calls
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("external_api", "External API Agent", config)
        self.api_config = config or {}
        self.session = requests.Session()
        self.session.timeout = 10  # 10 second timeout
        
        # API endpoints (can be configured)
        self.nvd_api_base = self.api_config.get("nvd_api_base", "https://services.nvd.nist.gov/rest/json/cves/2.0")
        self.virustotal_api = self.api_config.get("virustotal_api", None)
        self.abuseipdb_api = self.api_config.get("abuseipdb_api", None)
        self.shodan_api = self.api_config.get("shodan_api", None)
        
        # API keys (should be in environment variables or config)
        self.api_keys = {
            "virustotal": self.api_config.get("virustotal_api_key") or self._get_env_key("VIRUSTOTAL_API_KEY"),
            "abuseipdb": self.api_config.get("abuseipdb_api_key") or self._get_env_key("ABUSEIPDB_API_KEY"),
            "shodan": self.api_config.get("shodan_api_key") or self._get_env_key("SHODAN_API_KEY"),
        }
    
    def _get_env_key(self, key_name: str) -> Optional[str]:
        """Get API key from environment variable"""
        import os
        return os.environ.get(key_name)
    
    def get_capabilities(self) -> Dict[str, Any]:
        capabilities = {
            "external_sources": [],
            "api_enabled": False
        }
        
        if self.nvd_api_base:
            capabilities["external_sources"].append("NVD (CVE Database)")
        if self.api_keys.get("virustotal"):
            capabilities["external_sources"].append("VirusTotal")
        if self.api_keys.get("abuseipdb"):
            capabilities["external_sources"].append("AbuseIPDB")
        if self.api_keys.get("shodan"):
            capabilities["external_sources"].append("Shodan")
        
        capabilities["api_enabled"] = len(capabilities["external_sources"]) > 0
        return capabilities
    
    def fetch_cve_from_nvd(self, cve_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch CVE details from NVD API (NO RAG - direct API call)
        NVD API is free and doesn't require authentication
        """
        try:
            url = f"{self.nvd_api_base}?cveId={cve_id}"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            if data.get("vulnerabilities"):
                cve_data = data["vulnerabilities"][0]["cve"]
                return {
                    "id": cve_data.get("id"),
                    "description": cve_data.get("descriptions", [{}])[0].get("value", ""),
                    "severity": self._extract_severity(cve_data),
                    "cvss_score": self._extract_cvss(cve_data),
                    "published_date": cve_data.get("published", ""),
                    "references": [ref.get("url", "") for ref in cve_data.get("references", [])]
                }
        except Exception as e:
            self.logger.warning(f"Failed to fetch CVE {cve_id} from NVD: {e}")
        return None
    
    def search_cves_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search CVEs by keyword using NVD API (NO RAG - direct API call)
        """
        try:
            # NVD API search endpoint
            url = f"{self.nvd_api_base}?keywordSearch={keyword}&resultsPerPage={limit}"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            cves = []
            for vuln in data.get("vulnerabilities", [])[:limit]:
                cve_data = vuln["cve"]
                cves.append({
                    "id": cve_data.get("id"),
                    "description": cve_data.get("descriptions", [{}])[0].get("value", ""),
                    "severity": self._extract_severity(cve_data),
                    "cvss_score": self._extract_cvss(cve_data),
                    "published_date": cve_data.get("published", ""),
                })
            return cves
        except Exception as e:
            self.logger.warning(f"Failed to search CVEs for keyword '{keyword}': {e}")
            return []
    
    def check_ip_reputation(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Check IP reputation using AbuseIPDB API (NO RAG - direct API call)
        Requires API key
        """
        if not self.api_keys.get("abuseipdb"):
            self.logger.warning("AbuseIPDB API key not configured")
            return None
        
        try:
            url = "https://api.abuseipdb.com/api/v2/check"
            headers = {
                "Key": self.api_keys["abuseipdb"],
                "Accept": "application/json"
            }
            params = {
                "ipAddress": ip_address,
                "maxAgeInDays": 90,
                "verbose": ""
            }
            response = self.session.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get("data"):
                return {
                    "ip": ip_address,
                    "is_public": data["data"].get("isPublic", False),
                    "abuse_confidence": data["data"].get("abuseConfidencePercentage", 0),
                    "country": data["data"].get("countryCode", ""),
                    "usage_type": data["data"].get("usageType", ""),
                    "is_whitelisted": data["data"].get("isWhitelisted", False),
                    "reports_count": data["data"].get("totalReports", 0)
                }
        except Exception as e:
            self.logger.warning(f"Failed to check IP {ip_address} on AbuseIPDB: {e}")
        return None
    
    def check_hash_virustotal(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """
        Check file hash on VirusTotal (NO RAG - direct API call)
        Requires API key
        """
        if not self.api_keys.get("virustotal"):
            self.logger.warning("VirusTotal API key not configured")
            return None
        
        try:
            url = f"https://www.virustotal.com/vtapi/v2/file/report"
            params = {
                "apikey": self.api_keys["virustotal"],
                "resource": file_hash
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get("response_code") == 1:  # Found
                return {
                    "hash": file_hash,
                    "positives": data.get("positives", 0),
                    "total": data.get("total", 0),
                    "scan_date": data.get("scan_date", ""),
                    "permalink": data.get("permalink", "")
                }
        except Exception as e:
            self.logger.warning(f"Failed to check hash {file_hash} on VirusTotal: {e}")
        return None
    
    def _extract_severity(self, cve_data: Dict[str, Any]) -> str:
        """Extract severity from CVE data"""
        metrics = cve_data.get("metrics", {})
        if "cvssMetricV31" in metrics:
            base_severity = metrics["cvssMetricV31"][0].get("cvssData", {}).get("baseSeverity", "UNKNOWN")
            return base_severity
        elif "cvssMetricV30" in metrics:
            base_severity = metrics["cvssMetricV30"][0].get("cvssData", {}).get("baseSeverity", "UNKNOWN")
            return base_severity
        elif "cvssMetricV2" in metrics:
            base_severity = metrics["cvssMetricV2"][0].get("baseSeverity", "UNKNOWN")
            return base_severity
        return "UNKNOWN"
    
    def _extract_cvss(self, cve_data: Dict[str, Any]) -> float:
        """Extract CVSS score from CVE data"""
        metrics = cve_data.get("metrics", {})
        if "cvssMetricV31" in metrics:
            return metrics["cvssMetricV31"][0].get("cvssData", {}).get("baseScore", 0.0)
        elif "cvssMetricV30" in metrics:
            return metrics["cvssMetricV30"][0].get("cvssData", {}).get("baseScore", 0.0)
        elif "cvssMetricV2" in metrics:
            return metrics["cvssMetricV2"][0].get("baseScore", 0.0)
        return 0.0
    
    def check_software_vulnerability(self, software_name: str, version: str) -> List[SecurityAlert]:
        """
        Check software vulnerability using external APIs (NO RAG)
        """
        alerts = []
        
        # Search NVD for CVEs related to this software
        search_query = f"{software_name} {version}"
        cves = self.search_cves_by_keyword(search_query, limit=5)
        
        for cve in cves:
            severity_map = {
                "CRITICAL": AlertSeverity.CRITICAL,
                "HIGH": AlertSeverity.HIGH,
                "MEDIUM": AlertSeverity.MEDIUM,
                "LOW": AlertSeverity.LOW
            }
            severity = severity_map.get(cve.get("severity", "MEDIUM"), AlertSeverity.MEDIUM)
            
            alert = SecurityAlert(
                agent_id=self.agent_id,
                alert_type="external_cve_found",
                severity=severity,
                description=f"External CVE found: {cve['id']} - {cve['description'][:100]}",
                details={
                    "cve_id": cve["id"],
                    "software": software_name,
                    "version": version,
                    "cvss_score": cve.get("cvss_score", 0.0),
                    "source": "NVD API"
                }
            )
            alerts.append(alert)
        
        return alerts
    
    def analyze(self, data: Any) -> List[SecurityAlert]:
        """Analyze data using external APIs"""
        alerts = []
        
        if isinstance(data, dict):
            # Check IP addresses
            if "ip_address" in data:
                ip_info = self.check_ip_reputation(data["ip_address"])
                if ip_info and ip_info.get("abuse_confidence", 0) > 50:
                    alert = SecurityAlert(
                        agent_id=self.agent_id,
                        alert_type="suspicious_ip_external",
                        severity=AlertSeverity.HIGH,
                        description=f"IP {data['ip_address']} has {ip_info['abuse_confidence']}% abuse confidence",
                        details={"ip_info": ip_info, "source": "AbuseIPDB"}
                    )
                    alerts.append(alert)
            
            # Check file hashes
            if "file_hash" in data:
                hash_info = self.check_hash_virustotal(data["file_hash"])
                if hash_info and hash_info.get("positives", 0) > 0:
                    alert = SecurityAlert(
                        agent_id=self.agent_id,
                        alert_type="malicious_hash_external",
                        severity=AlertSeverity.CRITICAL,
                        description=f"Hash {data['file_hash']} detected by {hash_info['positives']}/{hash_info['total']} engines",
                        details={"hash_info": hash_info, "source": "VirusTotal"}
                    )
                    alerts.append(alert)
            
            # Check software vulnerabilities
            if "software" in data:
                for name, version in data["software"].items():
                    alerts.extend(self.check_software_vulnerability(name, version))
        
        return alerts
