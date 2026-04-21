#!/usr/bin/env python3
"""
Privacy Shield — Browser Hardening
Generate hardened configurations for Firefox and Chrome.
"""

from pathlib import Path
from typing import Dict, List
import json

class FirefoxHardener:
    """Generate prefs.js entries for maximum privacy."""

    HARDENING_PREFS = {
        # Disable WebRTC (prevent IP leaks)
        "media.peerconnection.enabled": False,
        "media.peerconnection.ice.default_address_only": False,
        "media.peerconnection.ice.no_host": True,

        # Disable telemetry
        "datareporting.healthreport.uploadEnabled": False,
        "datareporting.policy.dataSubmissionEnabled": False,
        "toolkit.telemetry.enabled": False,
        "toolkit.telemetry.unified": False,

        # Disable Pocket
        "extensions.pocket.enabled": False,
        "browser.pocket.enabled": False,

        # Disable sponsored content
        "browser.newtabpage.activity-stream.showSponsoredTopSites": False,
        "browser.newtabpage.activity-stream.showSponsored": False,

        # Enable DNS over HTTPS (if DoH provider configured)
        # "network.trr.mode": 2,  # requires DoH server

        # Disable autofill
        "browser.formfill.enable": False,

        # Disable password saving (use external manager)
        "signon.rememberSignons": False,

        # Disable 3rd party cookies
        "network.cookie.cookieBehavior": 1,  # 1 = accept only first-party

        # Clear history on close (optional)
        # "privacy.clearOnShutdown.cache": True,
        # "privacy.clearOnShutdown.cookies": True,

        # HTTPS-Only Mode
        "dom.security.https_only_mode": True,

        # Disable location sharing
        "geo.enabled": False,

        # Disable push notifications
        "permissions.default.desktop-notification": 2,

        # Disable WebGL fingerprinting
        "webgl.disabled": True,

        # Disable API for detecting plugins
        "plugin.scan.plid.all": False,

        # Resist fingerprinting (Tor's patches)
        "privacy.resistFingerprinting": True,
        "privacy.resistFingerprinting.exempted Domains": "",
        "privacy.resistFingerprinting.letterboxing": True,
    }

    @staticmethod
    def generate_prefs_file(output_path: Path, extra_prefs: Dict = None):
        """Write a prefs.js file with all hardening settings."""
        prefs = FirefoxHardener.HARDENING_PREFS.copy()
        if extra_prefs:
            prefs.update(extra_prefs)

        lines = [
            "// Privacy Shield — Firefox Hardened Configuration",
            "// Generated automatically — do not edit manually",
            "user_pref(\"general.config.obscure_value\", 0);",  # allow reading
        ]
        for key, value in prefs.items():
            if isinstance(value, bool):
                lines.append(f'user_pref("{key}", {str(value).lower()});')
            elif isinstance(value, int):
                lines.append(f'user_pref("{key}", {value});')
            else:
                lines.append(f'user_pref("{key}", "{value}");')

        output_path.write_text("\n".join(lines) + "\n")
        return output_path

class ChromeHardener:
    """Generate enterprise policies JSON for Chrome/Chromium."""

    POLICIES = {
        "IncognitoModeAvailability": 1,  # 1 = allowed, 0 = disabled, 2 = forced
        "MetricsReportingEnabled": False,
        "UrlKeyedAnonymizedDataCollectionEnabled": False,
        "SearchSuggestEnabled": False,
        "AutofillAddressEnabled": False,
        "AutofillCreditCardEnabled": False,
        "PasswordManagerEnabled": False,
        "SavedPasswordsEnabled": False,
        "ImportAutofillFormData": False,
        "DeveloperToolsDisabled": False,  # keep enabled for power users
        "BlockExternalExtensions": False,
        "SafeBrowsingEnabled": True,
        "SafeBrowsingForTrustedSourcesEnabled": False,
        "AllowOutdatedPlugins": False,
        "EnableGatesForVicaleEngineRecorder": False,
        "NetworkPredictionOptions": 2,  # 2 = disabled
        "QuicAllowed": False,
        "WebRtcEventLogCollectionAllowed": False,
        "WebRtcIpHandlingPolicy": "disable_non_proxied_udp",
    }

    @staticmethod
    def generate_policy_json(output_path: Path, extra_policies: Dict = None):
        policies = ChromeHardener.POLICIES.copy()
        if extra_policies:
            policies.update(extra_policies)

        policy_doc = {
            "Comment": "Privacy Shield — Chrome Hardened Policies",
            "policies": policies
        }
        output_path.write_text(json.dumps(policy_doc, indent=2) + "\n")
        return output_path

# Convenience
def harden_firefox(output_dir: Path = Path("./hardened_firefox")):
    output_dir.mkdir(parents=True, exist_ok=True)
    return FirefoxHardener.generate_prefs_file(output_dir / "prefs.js")

def harden_chrome(output_dir: Path = Path("./hardened_chrome")):
    output_dir.mkdir(parents=True, exist_ok=True)
    return ChromeHardener.generate_policy_json(output_dir / "policies.json")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate hardened browser configs")
    parser.add_argument("--firefox", action="store_true", help="Generate Firefox prefs.js")
    parser.add_argument("--chrome", action="store_true", help="Generate Chrome policies.json")
    parser.add_argument("--output", type=Path, default=Path("."), help="Output directory")
    args = parser.parse_args()

    if not (args.firefox or args.chrome):
        print("Select at least one: --firefox and/or --chrome")
        exit(1)

    if args.firefox:
        out = harden_firefox(args.output)
        print(f"✅ Firefox prefs.js generated: {out}")
    if args.chrome:
        out = harden_chrome(args.output)
        print(f"✅ Chrome policies.json generated: {out}")
