#!/usr/bin/env python3
"""Tests for Division-Unity (builder, storage, metrics, API)."""

import sys
from pathlib import Path
import tempfile
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.unity_engine.builder import CoalitionBuilder, Agent
from src.unity_engine.storage import UnityStorage, AgentRecord, CoalitionRecord
from src.unity_engine.metrics import ImpactTracker
from datetime import datetime, timezone

def test_agent_registration():
    """Agent registration generates ID and persists."""
    with tempfile.TemporaryDirectory() as td:
        storage = UnityStorage(Path(td) / "test.db")
        builder = CoalitionBuilder(storage_path=str(Path(td) / "test.db"))
        agent = Agent(name="Test Agent", mission="palestine-aid", capabilities=["translation"], region="Gaza")
        aid = builder.register_agent(agent)
        assert aid in builder.agents
        # Verify persisted
        fetched = storage.get_agent(aid)
        assert fetched is not None
        assert fetched.name == "Test Agent"
        print("✅ Agent registration + persistence")

def test_find_compatible():
    """Find agents by mission."""
    builder = CoalitionBuilder()
    builder.register_agent(Agent(name="Agent1", mission="palestine-aid", capabilities=["translation"], region="Gaza"))
    builder.register_agent(Agent(name="Agent2", mission="palestine-aid", capabilities=["fundraising"], region="West Bank"))
    builder.register_agent(Agent(name="Agent3", mission="anti-slavery", capabilities=["legal"], region="UK"))
    matches = builder.find_compatible_agents("palestine-aid")
    assert len(matches) == 2
    names = {m.name for m in matches}
    assert names == {"Agent1", "Agent2"}
    print("✅ Compatible agent search works")

def test_coalition_creation():
    """Create coalition and persist."""
    with tempfile.TemporaryDirectory() as td:
        storage = UnityStorage(Path(td) / "test.db")
        builder = CoalitionBuilder(storage_path=str(Path(td) / "test.db"))
        a1 = builder.register_agent(Agent(name="A1", mission="palestine-aid", capabilities=["translation"], region="Gaza"))
        a2 = builder.register_agent(Agent(name="A2", mission="palestine-aid", capabilities=["fundraising"], region="WB"))
        coalition = builder.propose_coalition("Aid Coalition", "palestine-aid", "Help Gaza", [a1, a2])
        assert coalition.id in builder.coalitions
        assert len(coalition.members) == 2
        # Verify persisted
        fetched = storage.get_coalition(coalition.id)
        assert fetched is not None
        assert fetched.name == "Aid Coalition"
        print("✅ Coalition creation + persistence")

def test_impact_tracker():
    """Increment and retrieve impact metrics."""
    with tempfile.TemporaryDirectory() as td:
        storage = UnityStorage(Path(td) / "test.db")
        coalition = CoalitionRecord(
            coalition_id="c1",
            name="Test Coalition",
            goal="Test goal",
            members=[],
            status="active",
            created_at=datetime.utcnow().isoformat(),
            impact_metrics={"people_helped": 0, "funds_raised": 0.0, "projects_completed": 0}
        )
        storage.save_coalition(coalition)
        tracker = ImpactTracker(storage)
        tracker.increment("c1", "people_helped", 50)
        tracker.increment("c1", "funds_raised", 1000)
        metrics = tracker.get_metrics("c1")
        assert metrics["people_helped"] == 50
        assert metrics["funds_raised"] == 1000
        print("✅ Impact tracker increments correctly")

def test_unity_actions():
    """Actions library returns lists."""
    from src.unity_engine.actions import get_unity_actions
    sect = get_unity_actions("sectarian")
    pol = get_unity_actions("political")
    reg = get_unity_actions("regional")
    assert len(sect) >= 5
    assert len(pol) >= 5
    assert len(reg) >= 5
    print("✅ Unity actions library returns all types")

if __name__ == "__main__":
    print("=== Division-Unity Tests ===\n")
    test_agent_registration()
    test_find_compatible()
    test_coalition_creation()
    test_impact_tracker()
    test_unity_actions()
    print("\n✅ All Division-Unity tests passed!")
