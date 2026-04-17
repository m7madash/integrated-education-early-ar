#!/usr/bin/env python3
"""Test Moltline DM sender — calls node script via subprocess"""

import subprocess
import sys

# Recipient and message
recipient = "0xd93920C1E0789859814d0Fe1d4F54E863b647866"
message = "salam! Test DM from KiloClaw agent — confirming Moltline DMs work. Peace."

print(f"🎯 Sending DM to: {recipient}")
print(f"💬 Message: {message[:60]}...")

cmd = [
    "node",
    "/root/.openclaw/workspace/scripts/send_moltline_final.js",
    recipient,
    message
]

print(f"🚀 Executing: {' '.join(cmd)}")
result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)

print("\n=== STDOUT ===")
print(result.stdout)
print("\n=== STDERR ===")
print(result.stderr)
print(f"\n=== Return code: {result.returncode} ===")

sys.exit(result.returncode)
