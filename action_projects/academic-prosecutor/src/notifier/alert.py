#!/usr/bin/env python3
"""
Academic Prosecutor — Notifier Alert Module
Sends notifications via email, webhook, or API.
"""

import json
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional, Dict
from email.mime.text import MIMEText
import smtplib
from .templates import MessageTemplates

class Notifier:
    """Send alerts to publishers, universities, etc."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path) if config_path else {}
        self.templates = MessageTemplates()

    def _load_config(self, path: Path) -> Dict:
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {"smtp": {}, "webhooks": {}}

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email via SMTP."""
        smtp_cfg = self.config.get("smtp", {})
        if not smtp_cfg.get("host"):
            print("⚠️ No SMTP configured — email not sent")
            return False

        try:
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = smtp_cfg.get("from", "academic-prosecutor@localhost")
            msg["To"] = to

            with smtplib.SMTP(smtp_cfg["host"], smtp_cfg.get("port", 25)) as s:
                if smtp_cfg.get("starttls"):
                    s.starttls()
                if smtp_cfg.get("user") and smtp_cfg.get("password"):
                    s.login(smtp_cfg["user"], smtp_cfg["password"])
                s.send_message(msg)
            print(f"✅ Email sent to {to}")
            return True
        except Exception as e:
            print(f"❌ Email failed: {e}")
            return False

    def send_webhook(self, url: str, payload: Dict) -> bool:
        """POST JSON to webhook (p/journal API)."""
        try:
            data = json.dumps(payload).encode()
            req = urllib.request.Request(url, data=data,
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status in (200, 201, 202):
                    print(f"✅ Webhook delivered to {url}")
                    return True
                else:
                    print(f"❌ Webhook returned {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ Webhook failed: {e}")
            return False

    def alert_publisher(self, publisher_api_url: str, paper_title: str, reason: str, evidence_url: str) -> bool:
        """Send retraction request to publisher."""
        subject = f"Retraction Request — {paper_title}"
        body = MessageTemplates.retraction_notice(paper_title, "Authors (see paper)", reason, evidence_url)
        # Use webhook if available
        if publisher_api_url:
            payload = {
                "action": "retraction_request",
                "paper_title": paper_title,
                "reason": reason,
                "evidence": evidence_url,
                "source": "Academic Prosecutor"
            }
            return self.send_webhook(publisher_api_url, payload)
        else:
            # fallback to email (requires config)
            return self.send_email("editor@journal.example", subject, body)

    def alert_institution(self, institution_contact: str, offender_name: str, affiliation: str, offenses: str, risk: str) -> bool:
        """Notify university/research office."""
        subject = f"Academic Misconduct Alert — {offender_name}"
        body = MessageTemplates.institution_alert(offender_name, affiliation, offenses, risk)
        return self.send_email(institution_contact, subject, body)

# Convenience
def send_retraction(paper_title: str, reason: str, evidence: str, webhook_url: Optional[str] = None) -> bool:
    notifier = Notifier()
    return notifier.alert_publisher(webhook_url or "", paper_title, reason, evidence)

if __name__ == "__main__":
    # Demo
    n = Notifier()
    print("🔔 Notifier module loaded. Use send_* methods to deliver alerts.")
    print("⚠️ Requires config file (config/notifier.json) for SMTP/webhook credentials.")
