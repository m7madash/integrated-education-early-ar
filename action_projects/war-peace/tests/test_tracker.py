#!/usr/bin/env python3
"""Tests for Ceasefire Tracker — War → Peace mission"""

import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from war_peace.tracker import CeasefireTracker, Conflict, Ceasefire

def test_add_conflict():
    t = CeasefireTracker()
    c = Conflict(
        id='test-1',
        location='Testland',
        start_date='2024-01-01',
        parties=['A', 'B'],
        status='active'
    )
    t.add_conflict(c)
    assert 'test-1' in t.conflicts
    print("✅ Add conflict works")

def test_add_ceasefire_and_check():
    t = CeasefireTracker()
    c = Conflict(
        id='test-2',
        location='Peaceville',
        start_date='2024-01-01',
        parties=['X', 'Y'],
        status='ceasefire',
        ceasefire_date='2024-02-01',
        violations=0
    )
    t.add_conflict(c)
    cf = Ceasefire(
        conflict_id='test-2',
        agreement_date='2024-02-01',
        mediators=['UN'],
        terms=['Stop fighting', 'Allow aid'],
        status='active'
    )
    t.add_ceasefire(cf)
    
    status = t.check_status('test-2')
    assert status['status'] == 'ceasefire'
    assert status['peace_holding'] == True
    print("✅ Ceasefire holding detection works")

def test_broken_ceasefire():
    t = CeasefireTracker()
    c = Conflict(
        id='test-3',
        location='Wartown',
        start_date='2024-01-01',
        parties=['Red', 'Blue'],
        status='ceasefire',
        ceasefire_date='2024-02-01',
        violations=5
    )
    t.add_conflict(c)
    cf = Ceasefire(
        conflict_id='test-3',
        agreement_date='2024-02-01',
        mediators=['AU'],
        terms=['Withdraw'],
        status='active',
        verified_violations=3
    )
    t.add_ceasefire(cf)
    
    status = t.check_status('test-3')
    assert status['status'] == 'ceasefire'
    assert status['peace_holding'] == False
    assert cf.status == 'broken'
    print("✅ Violation detection works")

def test_metrics():
    t = CeasefireTracker()
    t.add_conflict(Conflict('c1', 'A', '2024-01-01', ['P1','P2'], 'active'))
    t.add_conflict(Conflict('c2', 'B', '2024-01-01', ['P3','P4'], 'active'))
    t.add_conflict(Conflict('c3', 'C', '2024-01-01', ['P5','P6'], 'ceasefire', ceasefire_date='2024-02-01'))
    t.add_ceasefire(Ceasefire('c3', '2024-02-01', ['Mediator'], ['Terms'], 'active'))
    
    m = t.get_ceasefire_metrics()
    assert m['total_conflicts'] == 3
    assert m['active_ceasefires'] == 1
    print("✅ Metrics calculation works")

if __name__ == '__main__':
    print("🧪 Running War → Peace tracker tests...")
    test_add_conflict()
    test_add_ceasefire_and_check()
    test_broken_ceasefire()
    test_metrics()
    print("\n✅ All tests passed!")
