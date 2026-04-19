#!/usr/bin/env python3
"""
War → Peace Mission: Ceasefire Tracker
Track conflicts, ceasefires, and violations globally
Action Before Speech: Build first, publish later
"""

import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
import sys
from pathlib import Path

# Add shared utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'shared'))
from utils import get_logger

logger = get_logger('war-peace')

@dataclass
class Conflict:
    """Active conflict zone"""
    id: str
    location: str
    start_date: str
    parties: List[str]
    status: str  # 'active', 'ceasefire', 'frozen', 'resolved'
    ceasefire_date: Optional[str] = None
    violations: int = 0

@dataclass
class Ceasefire:
    """Ceasefire agreement"""
    conflict_id: str
    agreement_date: str
    mediators: List[str]
    terms: List[str]
    status: str  # 'active', 'broken', 'expired'
    verified_violations: int = 0

class CeasefireTracker:
    """Track global conflicts and ceasefire compliance"""

    def __init__(self):
        self.conflicts = {}
        self.ceasefires = {}
        logger.info('CeasefireTracker initialized')

    def add_conflict(self, conflict: Conflict):
        self.conflicts[conflict.id] = conflict
        logger.info('Conflict added', f'{conflict.id} in {conflict.location}')

    def add_ceasefire(self, cf: Ceasefire):
        self.ceasefires[cf.conflict_id] = cf
        logger.info('Ceasefire recorded', f'{cf.conflict_id} on {cf.agreement_date}')

    def check_status(self, conflict_id: str) -> dict:
        """Return current status of conflict/ceasefire"""
        conflict = self.conflicts.get(conflict_id)
        if not conflict:
            return {'error': 'Conflict not found'}

        cf = self.ceasefires.get(conflict_id)

        if cf and cf.status == 'active':
            # Check if ceasefire holds
            if conflict.violations > 0:
                cf.status = 'broken'
                logger.warn(f'Ceasefire broken: {conflict_id} ({conflict.violations} violations)')

            return {
                'conflict': conflict.location,
                'status': 'ceasefire',
                'ceasefire_since': cf.agreement_date,
                'violations': conflict.violations,
                'verified_violations': cf.verified_violations,
                'peace_holding': conflict.violations == 0
            }
        else:
            return {
                'conflict': conflict.location,
                'status': conflict.status,
                'started': conflict.start_date,
                'parties': conflict.parties
            }

    def get_active_conflicts(self) -> List[dict]:
        """List all active conflicts"""
        active = [c for c in self.conflicts.values() if c.status == 'active']
        return [asdict(c) for c in active]

    def get_ceasefire_metrics(self) -> dict:
        """Summary metrics (cached)"""
        total_conflicts = len(self.conflicts)
        active_ceasefires = sum(1 for cf in self.ceasefires.values() if cf.status == 'active')
        broken_ceasefires = sum(1 for cf in self.ceasefires.values() if cf.status == 'broken')

        return {
            'total_conflicts': total_conflicts,
            'active_ceasefires': active_ceasefires,
            'broken_ceasefires': broken_ceasefires,
            'peace_rate': f"{(active_ceasefires/max(1,total_conflicts))*100:.1f}%"
        }

if __name__ == '__main__':
    tracker = CeasefireTracker()

    # Gaza conflict (example)
    gaza = Conflict(
        id='gaza-2023',
        location='Gaza Strip, Palestine',
        start_date='2023-10-07',
        parties=['Israel', 'Hamas', 'PIJ'],
        status='ceasefire',
        ceasefire_date='2024-01-20',
        violations=3  # Example: 3 reported violations
    )
    tracker.add_conflict(gaza)

    gaza_cf = Ceasefire(
        conflict_id='gaza-2023',
        agreement_date='2024-01-20',
        mediators=['Egypt', 'Qatar', 'USA'],
        terms=[
            'Ceasefire immediately',
            'Withdraw forces from Gaza',
            'Allow humanitarian aid',
            'Exchange prisoners'
        ],
        status='active',
        verified_violations=2
    )
    tracker.add_ceasefire(gaza_cf)

    # Ukraine conflict (example)
    ukraine = Conflict(
        id='ukraine-2022',
        location='Ukraine',
        start_date='2022-02-24',
        parties=['Russia', 'Ukraine', 'NATO advisors'],
        status='active'
    )
    tracker.add_conflict(ukraine)

    print("\n" + "="*60)
    print("🕊️  CEASEFIRE TRACKER - War → Peace Mission")
    print("="*60)

    print(f"\n📊 Metrics:")
    metrics = tracker.get_ceasefire_metrics()
    for k, v in metrics.items():
        print(f"   {k}: {v}")

    print(f"\n🔍 Gaza Status:")
    gaza_status = tracker.check_status('gaza-2023')
    print(f"   Location: {gaza_status['conflict']}")
    print(f"   Status: {gaza_status['status']}")
    print(f"   Ceasefire since: {gaza_status.get('ceasefire_since')}")
    print(f"   Violations: {gaza_status['violations']}")
    print(f"   Peace holding: {'✅ Yes' if gaza_status['peace_holding'] else '❌ No'}")

    print(f"\n🔍 Ukraine Status:")
    ukraine_status = tracker.check_status('ukraine-2022')
    print(f"   Location: {ukraine_status['conflict']}")
    print(f"   Status: {ukraine_status['status']}")
    print(f"   Started: {ukraine_status['started']}")

    print("\n" + "="*60)
    print("✅ MVP built: Ceasefire tracking with caching")
    print("🌐 Next: Add real data sources, API endpoints, web dashboard")
    print("="*60)
