from collections import defaultdict
from typing import Dict

class MetricsCollector:
    """Performance metrics collector"""
    
    def __init__(self):
        self.agent_timings = defaultdict(list)
        self.incident_stats = {
            'total': 0,
            'by_severity': defaultdict(int),
            'by_service': defaultdict(int)
        }
    
    def track_agent_execution(self, agent_name: str, duration: float):
        """Track agent execution time"""
        self.agent_timings[agent_name].append(duration)
    
    def track_incident(self, severity: str, service: str):
        """Track incident statistics"""
        self.incident_stats['total'] += 1
        self.incident_stats['by_severity'][severity] += 1
        self.incident_stats['by_service'][service] += 1
    
    def get_agent_performance(self, agent_name: str) -> Dict:
        """Get performance metrics for an agent"""
        timings = self.agent_timings.get(agent_name, [])
        if not timings:
            return {}
        
        return {
            'avg_duration': sum(timings) / len(timings),
            'total_executions': len(timings),
            'min_duration': min(timings),
            'max_duration': max(timings)
        }
    
    def get_incident_statistics(self) -> Dict:
        """Get overall incident statistics"""
        return {
            'total_incidents': self.incident_stats['total'],
            'by_severity': dict(self.incident_stats['by_severity']),
            'by_service': dict(self.incident_stats['by_service'])
        }