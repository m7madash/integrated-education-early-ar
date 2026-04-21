#!/usr/bin/env python3
"""
Media Integrity — Main Detector Orchestrator
Combine all modules into unified analysis pipeline.
"""

import json
import mimetypes
from pathlib import Path
from typing import Dict, Optional, Union
from dataclasses import dataclass, asdict

from .image import ImageForensics, analyze_image as analyze_image_core
from .text import FakeNewsDetector, analyze_text as analyze_text_core
from .source import SourceReputation, analyze_source as analyze_source_core
from .video import VideoDeepfakeDetector, analyze_video as analyze_video_core
from .social import BotDetector, analyze_bot as analyze_bot_core, NetworkAnalyzer, analyze_network as analyze_network_core

@dataclass
class MediaIntegrityReport:
    """Comprehensive integrity report for any media item."""
    item_type: str  # 'image', 'text', 'video', 'account', 'network'
    item_identifier: str  # file path, URL, or account ID
    overall_integrity_score: float  # 0-1 (higher = more trustworthy)
    verdict: str  # PASS / SUSPICIOUS / FAIL
    component_results: Dict[str, Dict]
    critical_issues: List[str]
    recommendations: List[str]
    timestamp: str

class MediaDetector:
    """Orchestrate full media integrity analysis."""

    def __init__(self):
        self.image_analyzer = ImageForensics()
        self.text_analyzer = FakeNewsDetector()
        self.source_evaluator = SourceReputation()
        self.video_analyzer = VideoDeepfakeDetector()
        self.bot_detector = BotDetector()
        self.network_analyzer = NetworkAnalyzer()

    def analyze(self, item: Union[str, Dict], item_type: Optional[str] = None, context: Optional[Dict] = None) -> MediaIntegrityReport:
        """
        Unified analysis entrypoint.
        Args:
            item: file path (image/video), text string, account dict, or posts list
            item_type: 'image', 'text', 'video', 'account', 'network' (auto-detected if None)
            context: optional (source_url for text, author, etc.)
        """
        if item_type is None:
            item_type = self._detect_type(item)

        component_results = {}
        critical_issues = []
        recommendations = []
        integrity_score = 0.5  # default neutral

        if item_type == 'image':
            image_result = analyze_image_core(item) if isinstance(item, str) else self.image_analyzer.analyze(item)
            component_results['image_forensics'] = image_result
            integrity_score = 1 - image_result['manipulation_score']
            if image_result['likely_manipulated']:
                critical_issues.append("Image manipulation detected")
                recommendations.append("Do not share without verification")
            else:
                recommendations.append("Image appears authentic")

        elif item_type == 'text':
            text = item if isinstance(item, str) else item.get('text', '')
            source_url = context.get('source_url') if context else None
            text_result = analyze_text_core(text, source_url)
            component_results['fake_news'] = text_result
            integrity_score = 1 - text_result['manipulation_score']
            if text_result['is_likely_fake']:
                critical_issues.append("Fake news patterns detected")
                recommendations.append("Verify claims with fact-checkers")
            else:
                recommendations.append("Content appears credible")

        elif item_type == 'video':
            video_result = analyze_video_core(item) if isinstance(item, str) else self.video_analyzer.analyze(item)
            component_results['video_deepfake'] = video_result
            integrity_score = 1 - video_result['manipulation_score']
            if video_result['likely_deepfake']:
                critical_issues.append("Video likely deepfaked")
                recommendations.append("Do not share; seek original source")
            else:
                recommendations.append("Video appears authentic")

        elif item_type == 'account':
            account_data = item if isinstance(item, dict) else json.loads(item)
            bot_result = analyze_bot_core(account_data)
            component_results['bot_detection'] = bot_result
            integrity_score = 1 - bot_result['bot_score']
            if bot_result['is_likely_bot']:
                critical_issues.append("Account exhibits bot behavior")
                recommendations.append("Treat information from this account with caution")
            else:
                recommendations.append("Account appears human-operated")

        elif item_type == 'network':
            posts = item if isinstance(item, list) else json.loads(item)
            network_result = analyze_network_core(posts)
            component_results['network_coordination'] = network_result
            integrity_score = 1 - network_result['coordination_score']
            if network_result['coordination_score'] > 0.5:
                critical_issues.append("Coordinated inauthentic behavior detected")
                recommendations.append("Suspicious network activity — investigate further")
            else:
                recommendations.append("No obvious coordination detected")

        # Verdict
        if integrity_score >= 0.7:
            verdict = "PASS"
        elif integrity_score >= 0.4:
            verdict = "SUSPICIOUS"
        else:
            verdict = "FAIL"

        recommendations.append("Always cross-check with multiple reliable sources")
        recommendations.append("Report confirmed fakes to platform moderators")

        return MediaIntegrityReport(
            item_type=item_type,
            item_identifier=str(item)[:100],
            overall_integrity_score=round(integrity_score, 2),
            verdict=verdict,
            component_results=component_results,
            critical_issues=critical_issues,
            recommendations=recommendations,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    def _detect_type(self, item) -> str:
        """Infer item type from value."""
        if isinstance(item, str):
            if item.startswith('http'):
                # URL — guess from extension
                if any(ext in item.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    return 'image'
                elif any(ext in item.lower() for ext in ['.mp4', '.mov', '.avi', '.mkv']):
                    return 'video'
                else:
                    return 'text'  # article URL
            if Path(item).exists():
                mime, _ = mimetypes.guess_type(item)
                if mime:
                    if mime.startswith('image/'):
                        return 'image'
                    elif mime.startswith('video/'):
                        return 'video'
                    elif mime.startswith('text/') or mime == 'application/json':
                        # Could be account JSON or text file
                        try:
                            with open(item) as f:
                                data = json.load(f)
                            if isinstance(data, dict) and ('id' in data or 'username' in data):
                                return 'account'
                            elif isinstance(data, list):
                                return 'network'
                        except:
                            pass
                        return 'text'
            # else treat as plain text
            return 'text'
        elif isinstance(item, dict):
            if 'id' in item and 'username' in item:
                return 'account'
            elif 'posts' in item or 'content' in item:
                return 'network'
            else:
                return 'text'  # claim dict
        elif isinstance(item, list):
            return 'network'
        return 'text'

# Convenience
def analyze(item: Union[str, Dict, list], item_type: Optional[str] = None, context: Optional[Dict] = None) -> Dict:
    detector = MediaDetector()
    report = detector.analyze(item, item_type, context)
    return asdict(report)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Media Integrity Orchestrator")
    parser.add_argument("item", help="Item to analyze: file path, text, or JSON")
    parser.add_argument("--type", choices=['image', 'text', 'video', 'account', 'network'], help="Item type")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        # Try to parse as JSON first (for account/network)
        try:
            with open(args.item) as f:
                item = json.load(f)
            # auto-detect
            item_type = args.type or 'account' if isinstance(item, dict) else 'network'
        except:
            item = args.item
            item_type = args.type

        report = analyze(item, item_type)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"🔍 Media Integrity Report")
            print(f"Type: {report['item_type']}")
            print(f"Verdict: {report['verdict']} (score: {report['overall_integrity_score']})")
            print(f"Critical issues: {report['critical_issues']}")
            print(f"Recommendations: {report['recommendations']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
