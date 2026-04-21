#!/usr/bin/env python3
"""
Academic Prosecutor — Notification Templates
Pre-approved message templates for different violation levels/recipients.
"""

from typing import Dict

class MessageTemplates:
    """Templates for alerts to publishers, institutions, authors."""

    @staticmethod
    def retraction_notice(paper_title: str, authors: str, reason: str, evidence_url: str) -> str:
        return f"""Subject: Retraction Notice — {paper_title}

Dear Editor,

We are writing to formally request a retraction of the following paper:

Title: {paper_title}
Authors: {authors}
Reason: {reason}

Evidence: {evidence_url}

Our investigation, conducted under the Academic Prosecutor system, has determined that this paper violates standard research integrity policies.

Please confirm receipt and expected timeline for retraction.

Sincerely,
Academic Prosecutor
 Autonomous system for research integrity
"""

    @staticmethod
    def institution_alert(offender_name: str, affiliation: str, offenses: str, risk_level: str) -> str:
        return f"""Subject: Academic Misconduct Alert — {offender_name}

To: Research Integrity Office

We are notifying you of verified academic misconduct by an individual affiliated with your institution.

Name: {offender_name}
Affiliation: {affiliation}
Risk Level: {risk_level.upper()}

Offenses detected:
{offenses}

We have applied sanctions accordingly. Please investigate and take appropriate action.

Contact: academic-prosecutor@system.local (automated system)
"""

    @staticmethod
    def author_warning(paper_title: str, violation: str, corrective_action: str) -> str:
        return f"""Subject: Correction Required — {paper_title}

Dear Author,

Our system has detected a potential violation in your work:

Paper: {paper_title}
Issue: {violation}

Required action: {corrective_action}

If you believe this is an error, you may appeal within 14 days via the publisher's appeals process.

Otherwise, we expect compliance within 30 days.

Regards,
Academic Prosecutor
"""

    @staticmethod
    def summary_report(total_offenses: int, by_type: Dict[str, int], top_offenders: list) -> str:
        return f"""Academic Prosecutor — Weekly Summary

Total offenses processed: {total_offenses}
Breakdown by type:
{chr(10).join(f"  {k}: {v}" for k,v in by_type.items())}

Top risk offenders:
{chr(10).join(f"  - {o['name']} (score: {o['score']})" for o in top_offenders)}

Next steps: Continue monitoring, escalate critical cases.
"""

# Convenience
def render_template(template_name: str, **kwargs) -> str:
    templates = MessageTemplates()
    if hasattr(templates, template_name):
        return getattr(templates, template_name)(**kwargs)
    raise ValueError(f"Unknown template: {template_name}")
