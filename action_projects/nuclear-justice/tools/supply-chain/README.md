# Supply Chain Hunter — Tool 3 of Nuclear Justice

**Nonviolent supply chain disruption toolkit** for nuclear weapons proliferation networks.

---

## 🎯 What It Does

Tool 3 tracks, analyzes, and recommends lawful interventions against procurement networks that supply nuclear weapons programs. It operates in three stages:

1. **Tracker** — Builds a network map from open-source data (customs, shipping, corporate registries)
2. **Analyzer** — Identifies chokepoints, suspicious routes, timing patterns
3. **Disruptor** — Generates targeted, reversible intervention plans (legal, technical, informational)

All actions are **nonviolent**, **lawful**, and **discriminating** — no harm to civilians.

---

## 🔧 Installation

```bash
cd tools/supply-chain
# Python 3.8+ — no external dependencies
```

---

## 🚀 Usage

### Full demo pipeline
```bash
python3 supply_chain_hunter_cli.py --demo
```

### Step 1: Tracker (build network)
```bash
python3 supply_chain_hunter_cli.py --step tracker --output network.json
```
Or programmatically:
```python
from tracker.network_mapper import SupplyChainTracker
tracker = SupplyChainTracker()
tracker.add_entity(...)
tracker.add_shipment(...)
tracker.save(Path("network.json"))
```

### Step 2: Analyzer (detect patterns)
```bash
python3 supply_chain_hunter_cli.py --step analyzer --input network.json --output analysis.json
```

### Step 3: Disruptor (generate campaign)
```bash
python3 supply_chain_hunter_cli.py --step disruptor --input analysis.json --output campaign.md
```

Outputs:
- `campaign.md` — human-readable intervention plan
- `campaign.json` — machine-readable actions

---

## 🎮 Demo Output

Running `--demo` creates:
- `demo_network.json` — sample procurement network (5 entities, 2 shipments)
- `demo_analysis.json` — chokepoints, suspicious routes, timing patterns
- `demo_campaign_plan.md` — sequence of nonviolent interventions
- `demo_campaign.json` — structured action items

---

## 📂 Project Structure

```
tools/supply-chain/
├── supply_chain_hunter_cli.py   # Unified CLI entrypoint
├── README.md                    # This file
├── demo.sh                      # Demo runner (bash)
├── src/
│   ├── tracker/
│   │   └── network_mapper.py    # Entity/shipment/connection model
│   ├── analyzer/
│   │   └── pattern_detector.py  # Chokepoint detection, route analysis
│   └── disruptor/
│       └── campaign_planner.py  # Nonviolent intervention design
├── tests/ TBD
└── docs/ TBD
```

---

## ⚖️ Legal & Safety Principles

- ✅ **Nonviolence:** No physical destruction, no harm to civilians
- ✅ **Lawfulness:** All actions within national + international law
- ✅ **Discrimination:** Targets only procurement actors, not innocent workers
- ✅ **Reversibility:** Preferred actions are reversible (legal blocks, inspections)
- ✅ **Transparency:** Campaign plans document all actions and rationale

---

## 📊 Example Interventions

| Action Type | Example | Target |
|-------------|---------|--------|
| Legal block | File petition to court | Front company registration |
| Financial | Sanctions recommendation | High-risk entity |
| Technical | Customs inspection alert | Suspicious shipment route |
| Informational | Leak to investigative journalists | Evidence of illicit network |

---

**"Strike the supply chain, not the people."** — Supply Chain Hunter mantra
