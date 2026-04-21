#!/usr/bin/env python3
"""
Media Integrity — Image Forensics
Detect manipulated images using Error Level Analysis (ELA), metadata, and noise analysis.
"""

import io
import json
import base64
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

try:
    from PIL import Image, ImageChops, ImageStat
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import exifread
    HAS_EXIF = True
except ImportError:
    HAS_EXIF = False

@dataclass
class ImageAnalysisResult:
    """Results from image forensics analysis."""
    image_path: str
    manipulation_score: float  # 0-1, higher = more likely manipulated
    likely_manipulated: bool
    ela_histogram: Dict[str, float]  # mean, std of error levels
    metadata_anomalies: List[str]
    noise_consistency: float  # 0-1, lower = inconsistent (suspicious)
    edge_artifacts: float  # 0-1, higher = more artifacts
    recommendations: List[str]
    raw_ela_image: Optional[str] = None  # base64 encoded JPEG (optional)

class ImageForensics:
    """Run multiple forensics tests on an image."""

    def __init__(self, quality: int = 95):
        """
        Args:
            quality: JPEG quality for ELA (higher = more sensitive)
        """
        if not HAS_PIL:
            raise ImportError("PIL (Pillow) is required for image analysis")
        self.quality = quality

    def analyze(self, image_path: str, save_ela: bool = False) -> ImageAnalysisResult:
        """Comprehensive analysis of an image."""
        img = Image.open(image_path)
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 1. Error Level Analysis
        ela_score, ela_hist = self._error_level_analysis(img)

        # 2. Metadata check
        metadata_anomalies = self._check_metadata(image_path)

        # 3. Noise consistency
        noise_score = self._noise_consistency(img)

        # 4. Edge artifacts (simple: Laplacian variance)
        edge_score = self._edge_artifacts(img)

        # Combine into manipulation score (weighted)
        weights = {'ela': 0.4, 'noise': 0.3, 'edge': 0.2, 'metadata': 0.1}
        score = (ela_score * weights['ela'] +
                 (1 - noise_score) * weights['noise'] +  # lower noise_consistency = more suspicious
                 edge_score * weights['edge'] +
                 (1 if metadata_anomalies else 0) * weights['metadata'])

        likely_manipulated = score > 0.5

        recommendations = self._generate_recommendations(score, ela_score, noise_score, edge_score, metadata_anomalies)

        result = ImageAnalysisResult(
            image_path=image_path,
            manipulation_score=round(score, 3),
            likely_manipulated=likely_manipulated,
            ela_histogram=ela_hist,
            metadata_anomalies=metadata_anomalies,
            noise_consistency=round(noise_score, 3),
            edge_artifacts=round(edge_score, 3),
            recommendations=recommendations
        )
        return result

    def _error_level_analysis(self, img: Image.Image) -> Tuple[float, Dict[str, float]]:
        """
        ELA: Save image at high quality, resave at lower quality, compute difference.
        Manipulated areas often have different error levels.
        """
        # Save original to bytes at specified quality
        orig_bytes = io.BytesIO()
        img.save(orig_bytes, format='JPEG', quality=self.quality)
        orig_bytes.seek(0)
        orig = Image.open(orig_bytes)

        # Resave at slightly lower quality to amplify differences
        resaved_bytes = io.BytesIO()
        img.save(resaved_bytes, format='JPEG', quality=self.quality - 10)
        resaved_bytes.seek(0)
        resaved = Image.open(resaved_bytes)

        # Compute absolute difference
        diff = ImageChops.difference(img, resaved)
        extrema = diff.getextrema()  # (min, max) per channel
        # Use grayscale for simplicity
        gray = diff.convert('L')
        stat = ImageStat.Stat(gray)
        mean_error = stat.mean[0] / 255.0
        std_error = stat.stddev[0] / 255.0

        # Higher mean/std suggests manipulation
        ela_score = min(mean_error * 2 + std_error, 1.0)  # heuristic

        return ela_score, {'mean_error': round(mean_error, 4), 'std_error': round(std_error, 4)}

    def _check_metadata(self, image_path: str) -> List[str]:
        """Check EXIF metadata for anomalies."""
        anomalies = []
        if not HAS_EXIF:
            return ["exifread not installed"]
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                if tags:
                    # Check for editing software
                    software = str(tags.get('Image Software', ''))
                    if software and any(word in software.lower() for word in ['photoshop', 'gimp', 'affinity']):
                        anomalies.append(f"Editing software detected: {software}")
                    # Check DateTimeOriginal vs DateTimeDigitized mismatch
                    dt_orig = str(tags.get('EXIF DateTimeOriginal', ''))
                    dt_dig = str(tags.get('EXIF DateTimeDigitized', ''))
                    if dt_orig and dt_dig and dt_orig != dt_dig:
                        anomalies.append("DateTimeOriginal != DateTimeDigitized")
                    # Missing critical tags
                    if not tags.get('EXIF DateTimeOriginal'):
                        anomalies.append("Missing DateTimeOriginal (possible stripping)")
        except Exception as e:
            anomalies.append(f"Metadata read error: {e}")
        return anomalies

    def _noise_consistency(self, img: Image.Image) -> float:
        """
        Estimate noise consistency across the image.
        Splits image into 4 quadrants, measures variance in each.
        Low variance between quadrants = consistent noise = likely original.
        High variance = possibly spliced.
        """
        w, h = img.size
        quadrants = [
            img.crop((0, 0, w//2, h//2)),
            img.crop((w//2, 0, w, h//2)),
            img.crop((0, h//2, w//2, h)),
            img.crop((w//2, h//2, w, h))
        ]
        # Convert to grayscale and compute noise estimate (high-pass filter approx)
        means = []
        for q in quadrants:
            gray = q.convert('L')
            # Simple noise proxy: standard deviation of Laplacian (high frequency)
            # Using PIL: not super accurate but okay for demo
            stat = ImageStat.Stat(gray)
            means.append(stat.stddev[0])
        # Coefficient of variation across quadrants
        avg = sum(means) / len(means)
        if avg == 0:
            return 1.0
        variance = sum((m - avg) ** 2 for m in means) / len(means)
        cv = (variance ** 0.5) / avg  # relative std dev
        # Lower CV = more consistent noise = less suspicious
        consistency = max(0, 1 - cv)
        return consistency

    def _edge_artifacts(self, img: Image.Image) -> float:
        """
        Detect unnatural edges (common in AI-generated or poorly compressed images).
        Uses simple Laplacian variance.
        """
        gray = img.convert('L')
        # Approximate Laplacian with convolution (manual for speed)
        # kernel = [[1, -2, 1], [-2, 4, -2], [1, -2, 1]]
        # But we'll use a simpler method: high-pass via PIL filters
        try:
            from PIL import ImageFilter
            laplacian = gray.filter(ImageFilter.FIND_EDGES)
            stat = ImageStat.Stat(laplacian)
            mean_edge = stat.mean[0] / 255.0
            # Higher mean edge response could indicate over-sharpening or artifacts
            # But we need to compare to natural images; threshold heuristic:
            return min(mean_edge * 3, 1.0)  # scale up to be noticeable
        except ImportError:
            return 0.0

    @staticmethod
    def _generate_recommendations(score, ela, noise, edge, metadata_anomalies) -> List[str]:
        recs = []
        if score > 0.7:
            recs.append("High likelihood of manipulation — verify source and original")
        elif score > 0.4:
            recs.append("Suspicious features detected — further manual review recommended")
        else:
            recs.append("Image appears consistent with authentic origin")

        if ela > 0.3:
            recs.append("Error Level Analysis shows significant compression differences — possible editing")
        if noise < 0.5:
            recs.append("Noise pattern inconsistent across quadrants — may indicate splicing")
        if edge > 0.6:
            recs.append("Edge artifacts detected — could be AI-generated or over-processed")
        if metadata_anomalies:
            recs.append(f"Metadata issues: {', '.join(metadata_anomalies)}")
            recs.append("Check if editing software was used")
        return recs

# Convenience
def analyze_image(image_path: str) -> Dict:
    forensics = ImageForensics()
    result = forensics.analyze(image_path)
    # Convert to dict for JSON serialization (exclude raw_ela_image for brevity)
    d = asdict(result)
    d.pop('raw_ela_image', None)
    return d

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Image Forensics Analyzer")
    parser.add_argument("image", help="Path to image file")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    try:
        result = analyze_image(args.image)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"🔍 Image Forensics: {args.image}")
            print(f"Manipulation score: {result['manipulation_score']} ({'LIKELY FAKE' if result['likely_manipulated'] else 'LIKELY AUTHENTIC'})")
            print(f"ELA histogram: {result['ela_histogram']}")
            print(f"Noise consistency: {result['noise_consistency']}")
            print(f"Edge artifacts: {result['edge_artifacts']}")
            if result['metadata_anomalies']:
                print(f"Metadata anomalies: {', '.join(result['metadata_anomalies'])}")
            print("\nRecommendations:")
            for i, r in enumerate(result['recommendations'], 1):
                print(f" {i}. {r}")
    except Exception as e:
        print(f"❌ Error: {e}")
        if not HAS_PIL:
            print("Install: pip install Pillow")
        if not HAS_EXIF:
            print("Install: pip install exifread")
