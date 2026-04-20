"""
Supply Chain Tracker — Tool 3 of Nuclear Justice

Monitors procurement networks for nuclear weapons programs:
- Tracks shipping manifests, customs data, supplier databases
- Identifies front companies and transshipment routes
- Flags dual-use technology transfers

Data sources: open-source customs records, UN Comtrade, corporate registries
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime, date
from pathlib import Path

@dataclass
class Entity:
    name: str
    country: str
    type: str  # "manufacturer", "distributor", "shipping_agent", "front_company"
    risk_score: int = 0  # 0-10

@dataclass
class Shipment:
    tracking_id: str
    origin: str
    destination: str
    item_description: str
    hs_code: Optional[str] = None  # Harmonized System code
    quantity: int = 1
    units: str = "units"
    date: str = ""
    carrier: str = ""
    status: str = "in_transit"

@dataclass
class Connection:
    from_entity: str
    to_entity: str
    relation: str  # "supplies", "owns", "registered_director", "shared_address"
    strength: int = 5  # 1-10 confidence

class SupplyChainTracker:
    """Tracks nuclear procurement networks through open-source data."""

    def __init__(self):
        self.entities: List[Entity] = []
        self.shipments: List[Shipment] = []
        self.connections: List[Connection] = []
        self.risk_threshold = 7

    def add_entity(self, name: str, country: str, etype: str, risk: int = 0):
        self.entities.append(Entity(name, country, etype, risk))

    def add_shipment(self, tracking_id: str, origin: str, destination: str,
                     item_desc: str, hs_code: str = None, quantity: int = 1,
                     date_str: str = "", carrier: str = "", status: str = "in_transit"):
        self.shipments.append(Shipment(
            tracking_id, origin, destination, item_desc, hs_code,
            quantity, "units", date_str or date.today().isoformat(), carrier, status
        ))

    def add_connection(self, from_e: str, to_e: str, relation: str, strength: int = 5):
        self.connections.append(Connection(from_e, to_e, relation, strength))

    def flag_high_risk(self) -> List[Entity]:
        return [e for e in self.entities if e.risk_score >= self.risk_threshold]

    def find_routes(self, origin_country: str, dest_country: str) -> List[Shipment]:
        return [s for s in self.shipments if s.origin == origin_country and s.destination == dest_country]

    def generate_network_json(self) -> dict:
        return {
            "generated_date": datetime.now().isoformat(),
            "tool": "Supply Chain Hunter — Tracker",
            "entities": [asdict(e) for e in self.entities],
            "shipments": [asdict(s) for s in self.shipments],
            "connections": [asdict(c) for c in self.connections],
            "high_risk_entities": [asdict(e) for e in self.flag_high_risk()],
            "risk_threshold": self.risk_threshold
        }

    def save(self, output_path: Path):
        data = self.generate_network_json()
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return output_path

# Convenience: load from sanctions list (from Tool 2) to seed tracker
def seed_from_sanctions(sanctions_json_path: Path, tracker: SupplyChainTracker):
    """Populate tracker with entities from sanctions list."""
    data = json.loads(sanctions_json_path.read_text(encoding="utf-8"))
    for p in data.get("persons", []):
        tracker.add_entity(
            name=p["name"],
            country=p["country"],
            etype="individual",
            risk=p.get("risk_score", 5)
        )
    for o in data.get("organizations", []):
        tracker.add_entity(
            name=o["name"],
            country=o["country"],
            etype=o.get("org_type", "organization"),
            risk=o.get("risk_score", 5)
        )
    return tracker

if __name__ == "__main__":
    # Demo: build a sample network
    print("=" * 60)
    print("SUPPLY CHAIN HUNTER — Tool 3 Tracker Demo")
    print("=" * 60)

    tracker = SupplyChainTracker()

    # Add entities (sample nuclear procurement network)
    tracker.add_entity("ABC Trading LLC", "UAE", "distributor", risk=8)
    tracker.add_entity("XYZ Industries", "China", "manufacturer", risk=9)
    tracker.add_entity("Front Co Ltd", "Turkey", "front_company", risk=10)
    tracker.add_entity("Oceanic Shipping", "Malaysia", "shipping_agent", risk=6)
    tracker.add_entity("Dr. Ahmad Vahidi", "Iran", "individual", risk=9)

    # Add shipments
    tracker.add_shipment(
        tracking_id="TRK001",
        origin="China",
        destination="UAE",
        item_desc="CNC milling machines (dual-use)",
        hs_code="8459",
        quantity=2,
        date_str="2025-03-10",
        carrier="Oceanic Shipping",
        status="delivered"
    )
    tracker.add_shipment(
        tracking_id="TRK002",
        origin="UAE",
        destination="Turkey",
        item_desc="High-strength aluminum alloy plates",
        hs_code="7606",
        quantity=5000,
        date_str="2025-03-20",
        carrier="Oceanic Shipping",
        status="in_transit"
    )

    # Add connections
    tracker.add_connection("ABC Trading LLC", "Front Co Ltd", "supplies", strength=8)
    tracker.add_connection("XYZ Industries", "ABC Trading LLC", "sells_to", strength=9)
    tracker.add_connection("Front Co Ltd", "Dr. Ahmad Vahidi", "controlled_by", strength=7)

    # Save
    out = "demo_supply_chain_network.json"
    tracker.save(Path(out))
    print(f"✅ Network map generated: {out}")
    print(f"   Entities: {len(tracker.entities)}")
    print(f"   Shipments: {len(tracker.shipments)}")
    print(f"   High-risk flagged: {len(tracker.flag_high_risk())}")
    print("\nPreview:")
    with open(out) as f:
        print(f.read()[:600])
