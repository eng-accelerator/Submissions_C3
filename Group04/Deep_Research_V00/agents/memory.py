from typing import List, Dict

class ResearchMemory:
    """
    Manages the storage and retrieval of research findings.
    """
    
    def __init__(self):
        self.findings: List[Dict] = []
        self.context_history: List[str] = []

    def add_finding(self, finding: Dict):
        """
        Add a new validated finding to memory.
        """
        self.findings.append(finding)

    def get_context(self) -> str:
        """
        Retrieve all current findings as a context string.
        """
        return "\n".join([str(f) for f in self.findings])
    
    def to_dict(self):
        return {
            "findings": self.findings,
            "history": self.context_history
        }
