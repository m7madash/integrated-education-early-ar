#!/usr/bin/env python3
"""
Division → Unity — Persistent Storage
SQLite database for agent registry and coalitions.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict

@dataclass
class AgentRecord:
    """Agent stored in registry."""
    agent_id: str
    name: str
    mission: str
    capabilities: List[str]
    region: str
    contact: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

@dataclass
class CoalitionRecord:
    """Coalition stored in DB."""
    coalition_id: str
    name: str
    goal: str
    members: List[str]  # agent IDs
    status: str  # forming, active, paused, dissolved
    created_at: str
    impact_metrics: Dict  # people_helped, funds_raised, projects_completed

class UnityStorage:
    """SQLite backend for Division-Unity registry."""

    def __init__(self, db_path: Path = Path("data/unity.db")):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self):
        """Create tables if not exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    mission TEXT,
                    capabilities TEXT,  -- JSON array
                    region TEXT,
                    contact TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS coalitions (
                    coalition_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    goal TEXT,
                    members TEXT,  -- JSON array
                    status TEXT,
                    created_at TEXT,
                    impact_metrics TEXT  -- JSON object
                )
            """)
            conn.commit()

    # --- Agent CRUD ---

    def save_agent(self, agent: AgentRecord) -> bool:
        now = datetime.utcnow().isoformat()
        agent.created_at = agent.created_at or now
        agent.updated_at = now
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO agents
                (agent_id, name, mission, capabilities, region, contact, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent.agent_id,
                agent.name,
                agent.mission,
                json.dumps(agent.capabilities),
                agent.region,
                agent.contact,
                agent.created_at,
                agent.updated_at
            ))
            conn.commit()
        return True

    def get_agent(self, agent_id: str) -> Optional[AgentRecord]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM agents WHERE agent_id = ?", (agent_id,)).fetchone()
            if row:
                return AgentRecord(
                    agent_id=row[0],
                    name=row[1],
                    mission=row[2],
                    capabilities=json.loads(row[3]),
                    region=row[4],
                    contact=row[5],
                    created_at=row[6],
                    updated_at=row[7]
                )
        return None

    def list_agents(self, region: Optional[str] = None, capability: Optional[str] = None) -> List[AgentRecord]:
        query = "SELECT * FROM agents"
        params = []
        clauses = []
        if region:
            clauses.append("region = ?")
            params.append(region)
        if capability:
            # JSON contains capability (simple string match; could be improved)
            clauses.append("capabilities LIKE ?")
            params.append(f'%{capability}%')
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(query, params).fetchall()
            return [
                AgentRecord(
                    agent_id=r[0], name=r[1], mission=r[2],
                    capabilities=json.loads(r[3]), region=r[4],
                    contact=r[5], created_at=r[6], updated_at=r[7]
                ) for r in rows
            ]

    def delete_agent(self, agent_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM agents WHERE agent_id = ?", (agent_id,))
            conn.commit()
            return conn.total_changes > 0

    # --- Coalition CRUD ---

    def save_coalition(self, coalition: CoalitionRecord) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO coalitions
                (coalition_id, name, goal, members, status, created_at, impact_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                coalition.coalition_id,
                coalition.name,
                coalition.goal,
                json.dumps(coalition.members),
                coalition.status,
                coalition.created_at,
                json.dumps(coalition.impact_metrics)
            ))
            conn.commit()
        return True

    def get_coalition(self, coalition_id: str) -> Optional[CoalitionRecord]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM coalitions WHERE coalition_id = ?", (coalition_id,)).fetchone()
            if row:
                return CoalitionRecord(
                    coalition_id=row[0],
                    name=row[1],
                    goal=row[2],
                    members=json.loads(row[3]),
                    status=row[4],
                    created_at=row[5],
                    impact_metrics=json.loads(row[6])
                )
        return None

    def list_coalitions(self, status: Optional[str] = None) -> List[CoalitionRecord]:
        query = "SELECT * FROM coalitions"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(query, params).fetchall()
            return [
                CoalitionRecord(
                    coalition_id=r[0], name=r[1], goal=r[2],
                    members=json.loads(r[3]), status=r[4],
                    created_at=r[5], impact_metrics=json.loads(r[6])
                ) for r in rows
            ]

    def update_impact(self, coalition_id: str, metric: str, value: int) -> bool:
        """Increment an impact metric for a coalition."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT impact_metrics FROM coalitions WHERE coalition_id = ?", (coalition_id,)).fetchone()
            if not row:
                return False
            metrics = json.loads(row[0])
            metrics[metric] = metrics.get(metric, 0) + value
            conn.execute("UPDATE coalitions SET impact_metrics = ? WHERE coalition_id = ?",
                        (json.dumps(metrics), coalition_id))
            conn.commit()
            return True

# Convenience
def get_storage() -> UnityStorage:
    return UnityStorage()

if __name__ == "__main__":
    storage = UnityStorage()
    # Demo: create an agent
    agent = AgentRecord(
        agent_id="demo_001",
        name="Demo Agent",
        mission="education",
        capabilities=["translation", "fact-check"],
        region="global"
    )
    storage.save_agent(agent)
    print(f"✅ Saved agent: {storage.get_agent('demo_001').name}")

    # Demo: create coalition
    coalition = CoalitionRecord(
        coalition_id="coalition_001",
        name="Education Alliance",
        goal="Provide free education to 1000 children",
        members=["demo_001"],
        status="forming",
        created_at=datetime.utcnow().isoformat(),
        impact_metrics={"people_helped": 0, "funds_raised": 0.0, "projects_completed": 0}
    )
    storage.save_coalition(coalition)
    print(f"✅ Saved coalition: {storage.get_coalition('coalition_001').name}")
