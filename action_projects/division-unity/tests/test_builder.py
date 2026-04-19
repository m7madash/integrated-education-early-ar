#!/usr/bin/env python3
"""Tests for division-unity coalition builder."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.unity_engine.builder import CoalitionBuilder, Agent
from src.unity_engine.actions import get_unity_actions

def test_agent_registration():
    builder = CoalitionBuilder()
    agent = Agent("A1", "Test Agent", "palestine-aid", ["translation"], "Gaza")
    aid = builder.register_agent(agent)
    assert aid in builder.agents
    assert builder.agents[aid].name == "Test Agent"
    print("✅ Agent registration works")

def test_find_compatible():
    builder = CoalitionBuilder()
    builder.register_agent(Agent("A1", "Agent1", "palestine-aid", ["translation"], "Gaza"))
    builder.register_agent(Agent("A2", "Agent2", "palestine-aid", ["fundraising"], "West Bank"))
    builder.register_agent(Agent("A3", "Agent3", "anti-slavery", ["legal"], "UK"))
    matches = builder.find_compatible_agents("palestine-aid")
    assert len(matches) == 2
    print("✅ Compatible agent search works")

def test_coalition_creation():
    builder = CoalitionBuilder()
    a1 = builder.register_agent(Agent("A1", "Agent1", "palestine-aid", ["translation"], "Gaza"))
    a2 = builder.register_agent(Agent("A2", "Agent2", "palestine-aid", ["fundraising"], "WB"))
    coalition = builder.propose_coalition("Aid Coalition", "palestine-aid", "Help Gaza", [a1, a2])
    assert coalition.id in builder.coalitions
    assert len(coalition.members) == 2
    print("✅ Coalition creation works")

def test_unity_actions_exist():
    actions = get_unity_actions("sectarian")
    assert len(actions) >= 5
    assert isinstance(actions[0], str)
    print("✅ Unity actions retrieval works")

if __name__ == "__main__":
    print("=== Division-Unity Tests ===\n")
    test_agent_registration()
    test_find_compatible()
    test_coalition_creation()
    test_unity_actions_exist()
    print("\n✅ All 4 tests passed!")
