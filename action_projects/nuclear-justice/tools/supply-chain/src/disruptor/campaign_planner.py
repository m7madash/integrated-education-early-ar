"""
Supply Chain Disruptor — Tool 3 of Nuclear Justice

Implements nonviolent interventions to interrupt nuclear procurement:
- Legal: file petitions, send alerts to customs, trigger audits
- Technical: delay shipments via paperwork errors, misrouting flags (within legal bounds)
- Informational: leak evidence to press, inform watchdog NGOs

All actions are reversible, lawful, discriminate between combatants and civilians.
"""

import json
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from pathlib import Path

@dataclass
class Intervention:
    target: str
    action_type: str  # "legal", "technical", "informational"
    description: str
    expected_impact: str
    confidence: float = 0.5
    reversible: bool = True
    civilian_harm_risk: str = "none"  # "none", "low", "medium", "high"

class SupplyChainDisruptor:
    """Generates and executes nonviolent disruption campaigns."""

    def __init__(self, analysis_report: dict):
        self.analysis = analysis_report
        self.interventions: List[Intervention] = []

    def design_campaign(self) -> List[Intervention]:
        """Create a sequence of disruption actions based on analysis."""
        recs = self.analysis.get("disruption_recommendations", [])

        for rec in recs:
            action_type = rec.get("action_type", "legal_block")
            target = rec.get("target", "Unknown")

            if action_type == "legal_block":
                self.interventions.append(Intervention(
                    target=target,
                    action_type="legal",
                    description=f"File legal petition/cease-and-desist against {target}",
                    expected_impact="Halt pending shipments, freeze assets",
                    confidence=rec.get("confidence", 0.6),
                    reversible=True,
                    civilian_harm_risk="none"
                ))

            elif action_type == "financial_block":
                self.interventions.append(Intervention(
                    target=target,
                    action_type="legal",
                    description=f"Submit sanctions recommendation for {target} to relevant authorities",
                    expected_impact="Asset freeze, transaction blocking",
                    confidence=rec.get("confidence", 0.7),
                    reversible=True,
                    civilian_harm_risk="none"
                ))

            elif action_type == "inspection_alert":
                self.interventions.append(Intervention(
                    target=target,
                    action_type="technical",
                    description=f"Alert customs to inspect all cargo on route {target}",
                    expected_impact="Delays, increased scrutiny, seizure of illicit goods",
                    confidence=0.8,
                    reversible=True,
                    civilian_harm_risk="low"  # may affect legitimate trade
                ))

        return self.interventions

    def generate_campaign_plan(self, output_path: Path):
        """Write a structured campaign plan (Markdown) for human/NGO execution."""
        lines = []
        lines.append("# Supply Chain Disruption Campaign — Tool 3, Nuclear Justice")
        lines.append(f"**Generated:** {datetime.now().isoformat()}")
        lines.append("---")
        lines.append("")
        lines.append("## Campaign Overview")
        lines.append("This plan uses **nonviolent, lawful interventions** to interrupt nuclear weapons procurement networks.")
        lines.append("All actions are reversible and discriminate between military targets and civilian infrastructure.")
        lines.append("")
        lines.append("## Intervention Sequence")
        lines.append("")

        for i, intervention in enumerate(self.interventions, 1):
            lines.append(f"### Step {i}: {intervention.action_type.upper()} — {intervention.target}")
            lines.append(f"**Action:** {intervention.description}")
            lines.append(f"**Expected impact:** {intervention.expected_impact}")
            lines.append(f"**Confidence:** {int(intervention.confidence * 100)}%")
            lines.append(f"**Reversible:** {'Yes' if intervention.reversible else 'No — evaluate carefully'}")
            lines.append(f"**Civilian harm risk:** {intervention.civilian_harm_risk}")
            lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("## Safety & Ethics Checklist")
        lines.append("- [ ] All actions comply with international law (UN Charter, IHL)")
        lines.append("- [ ] No physical destruction of civilian infrastructure")
        lines.append("- [ ] No harm to innocent workers or bystanders")
        lines.append("- [ ] Actions are reversible where possible")
        lines.append("- [ ] Civilian collateral < 1% of expected military benefit")
        lines.append("")
        lines.append("## Monitoring & Adaptation")
        lines.append("Track results daily. If a action causes unintended harm, **STOP** and reassess.")
        lines.append("")

        md = "\n".join(lines)
        output_path.write_text(md, encoding="utf-8")
        return output_path

    def save_json(self, output_path: Path):
        data = {
            "generated": datetime.now().isoformat(),
            "tool": "Supply Chain Hunter — Disruptor",
            "interventions": [i.__dict__ for i in self.interventions],
            "total_interventions": len(self.interventions)
        }
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return output_path

# Convenience wrapper
def build_disruption_campaign(analysis_json_path: Path, output_md: str, output_json: str):
    data = json.loads(analysis_json_path.read_text(encoding="utf-8"))
    disruptor = SupplyChainDisruptor(data)
    disruptor.design_campaign()
    disruptor.generate_campaign_plan(Path(output_md))
    disruptor.save_json(Path(output_json))
    return disruptor

if __name__ == "__main__":
    print("=" * 60)
    print("SUPPLY CHAIN HUNTER — Tool 3: Disruptor Demo")
    print("=" * 60)
    print("Waiting for analysis report from Analyzer...")
    print("(Run analyzer first, then feed its output to this disruptor)")
