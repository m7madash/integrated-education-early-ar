"""
Adhan Trigger — Fajr Observer Agent

Plays Adhan sound and sends notifications when true dawn is confirmed.
Supports: local audio, Telegram bot, webhook, optional MP3 file.
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

class AdhanTrigger:
    """Triggers Adhan via multiple channels."""

    def __init__(self,
                 audio_file: str = "data/azan_fajr.mp3",
                 telegram_bot_token: Optional[str] = None,
                 telegram_chat_id: Optional[str] = None,
                 webhook_url: Optional[str] = None,
                 dry_run: bool = True):
        self.dry_run = dry_run
        self.audio_file = Path(audio_file)
        self.telegram_bot_token = telegram_bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = telegram_chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.webhook_url = webhook_url

        # Verify audio file exists
        if not self.audio_file.exists():
            print(f"⚠️  Adhan audio not found: {audio_file}")
            print("   Place an MP3 file there or set custom audio_file.")

    def trigger(self, message: str = "الفجر الصادق ظهر — حان وقت صلاة الفجر"):
        """Main entry: execute all configured notification channels."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n🕌 ADHAN TRIGGER at {timestamp}")
        print(f"   {message}")

        if self.dry_run:
            print("   [DRY RUN — no actions taken]")
            return

        results = []
        results.append(self._play_audio())
        results.append(self._send_telegram(message))
        results.append(self._send_webhook(message))
        print(f"   Channels triggered: {sum(1 for r in results if r)}")

    def _play_audio(self) -> bool:
        """Play Adhan MP3 using system player."""
        if not self.audio_file.exists():
            return False
        try:
            # Try multiple players
            for player in ["mpv", "mplayer", "aplay", "ffplay"]:
                try:
                    subprocess.run([player, "-really-quiet", str(self.audio_file)],
                                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"   🔊 Adhan played via {player}")
                    return True
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
            print("   ⚠️  No audio player found (mpv/mplayer/aplay/ffplay)")
            return False
        except Exception as e:
            print(f"   ❌ Audio error: {e}")
            return False

    def _send_telegram(self, message: str) -> bool:
        """Send Adhan message via Telegram bot."""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return False
        try:
            import requests
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": f"🕌 *Fajr Observer*\n\n{message}",
                "parse_mode": "Markdown"
            }
            r = requests.post(url, json=payload, timeout=10)
            if r.status_code == 200:
                print("   📱 Telegram notification sent")
                return True
            else:
                print(f"   ⚠️  Telegram error: {r.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Telegram failed: {e}")
            return False

    def _send_webhook(self, message: str) -> bool:
        """POST to a custom webhook (e.g., Home Assistant, IFTTT)."""
        if not self.webhook_url:
            return False
        try:
            import requests
            r = requests.post(self.webhook_url, json={"fajr": True, "message": message}, timeout=5)
            return r.status_code < 400
        except Exception as e:
            print(f"   ❌ Webhook failed: {e}")
            return False


if __name__ == "__main__":
    print("Adhan Trigger — Test Mode")
    print("Use: python3 -m src.notification.azan_trigger [--live]")
    import sys
    dry = True
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        dry = False
    trigger = AdhanTrigger(dry_run=dry)
    trigger.trigger()
