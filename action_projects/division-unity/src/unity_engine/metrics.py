#!/usr/bin/env python3
"""
Division → Unity — Impact Metrics
Track people helped, funds raised, projects completed per coalition.
"""

from typing import Dict, List, Optional
from datetime import datetime
from .storage import UnityStorage

class ImpactTracker:
    """Track and update impact metrics for coalitions."""

    METRICS = ["people_helped", "funds_raised", "projects_completed"]

    def __init__(self, storage: UnityStorage = None):
        self.storage = storage or UnityStorage()

    def increment(self, coalition_id: str, metric: str, amount: int = 1) -> bool:
        """Increment a metric for a coalition."""
        if metric not in self.METRICS:
            raise ValueError(f"Unknown metric: {metric}. Use: {self.METRICS}")
        return self.storage.update_impact(coalition_id, metric, amount)

    def get_metrics(self, coalition_id: str) -> Dict[str, int]:
        """Get current metrics for a coalition."""
        coalition = self.storage.get_coalition(coalition_id)
        if coalition:
            return coalition.impact_metrics
        return {}

    def total_impact(self, coalition_ids: List[str] = None) -> Dict[str, int]:
        """Sum metrics across coalitions (or all if None)."""
        totals = {m: 0 for m in self.METRICS}
        if coalition_ids:
            coalitions = [self.storage.get_coalition(cid) for cid in coalition_ids]
        else:
            coalitions = self.storage.list_coalitions()
        for c in coalitions:
            for metric, value in c.impact_metrics.items():
                totals[metric] = totals.get(metric, 0) + value
        return totals

# Convenience
def record_impact(coalition_id: str, metric: str, amount: int = 1) -> bool:
    tracker = ImpactTracker()
    return tracker.increment(coalition_id, metric, amount)

if __name__ == "__main__":
    tracker = ImpactTracker()
    # Demo: increment
    print("Impact metrics demo:")
    print("Available metrics:", ImpactTracker.METRICS)
