#!/usr/bin/env python3
"""War → Peace CLI — Ceasefire Tracker command-line interface"""

from war_peace.tracker import CeasefireTracker, Conflict, Ceasefire
import sys

def demo():
    """Run demo with sample conflicts"""
    tracker = CeasefireTracker()
    
    # Gaza
    gaza = Conflict(
        id='gaza-2023',
        location='Gaza Strip, Palestine',
        start_date='2023-10-07',
        parties=['Israel', 'Hamas'],
        status='ceasefire',
        ceasefire_date='2024-01-20',
        violations=3
    )
    tracker.add_conflict(gaza)
    
    gaza_cf = Ceasefire(
        conflict_id='gaza-2023',
        agreement_date='2024-01-20',
        mediators=['Egypt', 'Qatar', 'USA'],
        terms=['Immediate ceasefire', 'Aid access', 'Prisoner exchange'],
        status='active',
        verified_violations=2
    )
    tracker.add_ceasefire(gaza_cf)
    
    # Ukraine
    ukraine = Conflict(
        id='ukraine-2022',
        location='Ukraine',
        start_date='2022-02-24',
        parties=['Russia', 'Ukraine'],
        status='active'
    )
    tracker.add_conflict(ukraine)
    
    # Print status
    print("\n" + "="*60)
    print("🕊️  Ceasefire Tracker — War → Peace")
    print("="*60)
    
    metrics = tracker.get_ceasefire_metrics()
    print("\n📊 Global Metrics:")
    for k, v in metrics.items():
        print(f"   {k}: {v}")
    
    for cid in tracker.conflicts:
        st = tracker.check_status(cid)
        print(f"\n🔍 {st['conflict']}:")
        print(f"   Status: {st['status']}")
        if st['status'] == 'ceasefire':
            print(f"   Since: {st.get('ceasefire_since')}")
            print(f"   Violations: {st['violations']}")
            print(f"   Peace holding: {'✅' if st['peace_holding'] else '❌'}")
        else:
            print(f"   Started: {st['started']}")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    demo()
