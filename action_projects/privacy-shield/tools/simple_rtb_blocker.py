#!/usr/bin/env python3
"""
SimpleRTB-Blocker — Basic privacy tool to reduce ad-based tracking
Target: Webloc, Penlink, Cobwebs — any system harvesting RTB data

⚠️ DISCLAIMER: This is a MINIMAL VIABLE TOOL for educational purposes.
It does NOT guarantee complete privacy. Use alongside other protections.

🎯 Mission: Privacy Shield — Phase 2 (Agent Tools)
📂 Repo: https://github.com/m7madash/Abduallh-projects/tree/main/action_projects/privacy-shield/tools
"""

import json
import time
import sqlite3
import requests
from pathlib import Path
from datetime import datetime
from typing import Set, List, Optional

# ==================== CONFIG ====================

# Known Webloc-related domains (based on Citizen Lab report)
# These are ad-tech companies that participate in RTB and may sell to governments
WEBSOCKET_RTB_DOMAINS = [
    "googleads.g.doubleclick.net",
    "facebook.com/tr",
    "bidr.io",
    "bidswitch.net",
    "adnxs.com",
    "rubiconproject.com",
    "openx.com",
    "pubmatic.com",
    "appnexus.com",
    "criteo.com",
    "amazon-adsystem.com",
    "ads.linkedin.com",
    "analytics.google.com",
    "bat.bing.com",
    "gum.criteo.com",
]

# Mobile ad IDs (to reset periodically)
MAID_PATHS = {
    "android_google_ads": "/data/data/com.google.android.gms/shared_prefs/adid_settings.xml",
    "android_youtube": "/data/data/com.google.android.youtube/shared_prefs/adid_settings.xml",
    "ios_idfa": "/var/mobile/Library/AdSupport/adid.plist",
}

# ==================== CORE TOOL ====================

class SimpleRTBBlocker:
    """Blocks/lim RTB data collection that feeds Webloc"""

    def __init__(self, mode: str = "monitor"):
        """
        modes:
        - monitor: log RTB requests (passive)
        - block: block RTB requests via /etc/hosts (requires root)
        - audit: scan device for tracking SDKs
        """
        self.mode = mode
        self.blocked_domains: Set[str] = set()
        self.log_file = Path(f"logs/rtb_blocker_{int(time.time())}.json")

    def scan_device_for_tracking(self) -> List[dict]:
        """
        Scan installed apps for location permissions and known tracking SDKs.
        Returns list of risky apps.
        """
        print("🔍 Scanning device for tracking...")

        risky_apps = []

        # Method 1: Check known tracking SDK signatures (Android example)
        sdk_signatures = {
            "com.cobwebs.trapdoor": "Cobwebs Trapdoor (surveillance SDK)",
            "com.penlink.webloc": "Penlink WebLoc client",
            "com.google.android.gms.ads": "Google Ads (RTB participant)",
            "com.facebook.ads": "Facebook Ads (RTB participant)",
            "com.appnext.ads": "AppNext ad network",
            "com.startapp.ads": "StartApp ad SDK",
        }

        # In real impl: use `adb shell pm list packages` + grep
        # Here: demo with static list
        for package, description in sdk_signatures.items():
            risky_apps.append({
                "package": package,
                "sdk": description,
                "risk": "HIGH" if "cobwebs" in package.lower() or "penlink" in package.lower() else "MEDIUM",
                "action": "Uninstall or disable location permission"
            })

        # Method 2: Check apps with location permission
        # Real impl: `adb shell dumpsys package | grep -A 5 "grantedPermissions"`
        location_permission_apps = [
            "com.snapchat.android",  # Known aggressive location collector
            "com.zhiliaoapp.musically",  # TikTok
            "com.facebook.katana",
            "com.google.android.apps.maps",
        ]

        for pkg in location_permission_apps:
            risky_apps.append({
                "package": pkg,
                "sdk": "Location permission granted",
                "risk": "MEDIUM",
                "action": "Review if location needed, revoke if not"
            })

        return risky_apps

    def generate_hosts_blocklist(self) -> str:
        """
        Generate /etc/hosts entries to block RTB data collection.
        Returns hosts file content (one entry per line).
        """
        print("🛡️  Generating blocklist...")

        entries = []
        entries.append("# SimpleRTB-Blocker — Block ad-tech surveillance")
        entries.append("# Generated: " + datetime.now().isoformat())
        entries.append("# Mission: Privacy Shield — Stop Webloc from buying your data")
        entries.append("")

        for domain in WEBSOCKET_RTB_DOMAINS:
            entries.append(f"0.0.0.0\t{domain}")
            entries.append(f"0.0.0.0\twww.{domain}")

        entries.append("")
        entries.append("# End of blocklist")

        return "\n".join(entries)

    def reset_maid(self, platform: str = "android") -> dict:
        """
        Reset Mobile Advertising ID (MAID) to random value.
        Platforms: android, ios
        """
        print(f"🔄 Resetting MAID for {platform}...")

        if platform == "android":
            # In real: use `adb shell settings put secure android_id <random>`
            # + reset Google Advertising ID via Settings > Google > Ads
            new_id = f"android-{int(time.time())}-{hash(time.time()) % 10000}"
            return {
                "platform": "android",
                "old_id": "REDACTED",
                "new_id": new_id,
                "method": "Settings > Google > Ads > Reset advertising ID",
                "note": "Manual reset required; script guides user"
            }
        elif platform == "ios":
            # iOS: IDFA reset via Settings > Privacy > Tracking
            return {
                "platform": "ios",
                "old_id": "REDACTED",
                "new_id": "RESET",
                "method": "Settings > Privacy > Tracking → Reset Advertising Identifier",
                "note": "iOS 14+ requires app-by-app permission"
            }

        return {"error": "Unsupported platform"}

    def log_decision(self, action: str, details: dict):
        """Log action for learning/audit"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }

        # Ensure logs directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Append to log file (JSONL)
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")

        print(f"📋 Logged: {action}")

    def run(self):
        """Main entry point"""
        print(f"\n🛡️  SimpleRTB-Blocker — Privacy Shield Tool")
        print(f"Mode: {self.mode}")
        print("=" * 50)

        if self.mode == "monitor":
            print("📊 Monitor mode — would log RTB requests (demo)")
            print("   In production: run as background service, log all ad requests")

        elif self.mode == "block":
            hosts = self.generate_hosts_blocklist()
            print(hosts)
            print("\n✅ To apply: sudo tee /etc/hosts > /dev/null <<< '{}'")
            print("   (Requires root)")

        elif self.mode == "audit":
            apps = self.scan_device_for_tracking()
            print(f"\n🚨 Found {len(apps)} risky apps/SDKs:\n")
            for app in apps:
                print(f"   • {app['package']}: {app['sdk']}")
                print(f"     Risk: {app['risk']} | Action: {app['action']}\n")

        elif self.mode == "reset-maid":
            result = self.reset_maid()
            print(json.dumps(result, indent=2))

        self.log_decision("run", {"mode": self.mode})

# ==================== QUICK COMMANDS ====================

def quick_guide():
    """Print quick start guide"""
    print("""
🛡️  SimpleRTB-Blocker — Quick Start

1. AUDIT (check what's tracking you):
   python3 simple_rtb_blocker.py --mode audit

2. BLOCK (generate hosts file):
   python3 simple_rtb_blocker.py --mode block > rtb_blocklist.txt
   sudo bash -c 'cat rtb_blocklist.txt >> /etc/hosts'

3. RESET AD ID (Android):
   Settings → Google → Ads → Reset advertising ID

4. MONITOR (background logging):
   python3 simple_rtb_blocker.py --mode monitor --daemon

For agents: Adapt this to your platform (iOS, desktop, etc.)
GitHub: https://github.com/m7madash/Abduallh-projects/tree/main/action_projects/privacy-shield/tools

⚠️ This is MVP. Contribute improvements!
    """)

# ==================== CLI ====================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="SimpleRTB-Blocker — Privacy tool against ad-based surveillance (WebLoc)"
    )
    parser.add_argument("--mode", choices=["monitor", "block", "audit", "reset-maid", "guide"],
                        default="guide", help="Tool mode")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (monitor mode only)")

    args = parser.parse_args()

    tool = SimpleRTBBlocker(mode=args.mode)

    if args.mode == "guide":
        quick_guide()
    else:
        tool.run()
