#!/usr/bin/env python3
"""
Media Integrity — Video Deepfake Detection
Detect AI-generated or manipulated videos using multiple signals.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    import dlib
    HAS_DLIB = True
except ImportError:
    HAS_DLIB = False

@dataclass
class VideoAnalysisResult:
    """Results from video forensics."""
    video_path: str
    manipulation_score: float  # 0-1
    likely_deepfake: bool
    frame_artifacts: float  # 0-1
    blink_inconsistency: float  # 0-1 (higher = weird blink patterns)
    lip_sync_score: float  # 0-1 (lower = misaligned)
    audio_visual_desync: float  # seconds of desync
    metadata_anomalies: List[str]
    recommendations: List[str]

class VideoDeepfakeDetector:
    """Detect deepfakes in video files."""

    def __init__(self, sample_rate: int = 5):
        """
        Args:
            sample_rate: analyze every Nth frame (default 5 to speed up)
        """
        self.sample_rate = sample_rate
        self.face_detector = None
        self.landmark_predictor = None
        if HAS_CV2 and HAS_DLIB:
            self.face_detector = dlib.get_frontal_face_detector()
            self.landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        # Fallback: simple methods without dlib

    def analyze(self, video_path: str) -> VideoAnalysisResult:
        """Comprehensive video deepfake detection."""
        if not HAS_CV2:
            raise ImportError("OpenCV (cv2) is required for video analysis")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Collect frames for analysis
        frames = []
        frame_indices = range(0, total_frames, self.sample_rate)
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
        cap.release()

        # 1. Frame artifacts (compression, noise differences)
        artifact_score = self._detect_frame_artifacts(frames)

        # 2. Blink inconsistency (if face landmarks available)
        blink_score = self._detect_blink_inconsistency(frames) if self.face_detector else 0.5

        # 3. Lip-sync (basic: mouth region motion vs audio amplitude placeholder)
        lip_sync_score = self._estimate_lip_sync(frames)  # placeholder

        # 4. Audio-visual desync (requires audio; skip for now)
        audio_desync = 0.0  # not implemented without audio extraction

        # 5. Metadata anomalies
        metadata_anomalies = self._check_metadata(video_path)

        # Combine
        weights = {'artifact': 0.3, 'blink': 0.3, 'lip': 0.2, 'audio': 0.2}
        score = (artifact_score * weights['artifact'] +
                 blink_score * weights['blink'] +
                 (1 - lip_sync_score) * weights['lip'] +  # lower lip_sync = more suspicious
                 audio_desync * weights['audio'])

        likely_deepfake = score > 0.5

        recommendations = self._generate_recommendations(score, artifact_score, blink_score, lip_sync_score, metadata_anomalies)

        return VideoAnalysisResult(
            video_path=video_path,
            manipulation_score=round(score, 3),
            likely_deepfake=likely_deepfake,
            frame_artifacts=round(artifact_score, 3),
            blink_inconsistency=round(blink_score, 3),
            lip_sync_score=round(lip_sync_score, 3),
            audio_visual_desync=round(audio_desync, 3),
            metadata_anomalies=metadata_anomalies,
            recommendations=recommendations
        )

    def _detect_frame_artifacts(self, frames: List) -> float:
        """
        Detect inconsistencies between consecutive frames.
        Deepfakes often have unnatural frame-to-frame noise patterns.
        """
        if len(frames) < 2:
            return 0.0
        diffs = []
        for i in range(len(frames) - 1):
            # Convert to grayscale
            gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY)
            # Compute mean squared error
            mse = np.mean((gray1.astype("float") - gray2.astype("float")) ** 2)
            diffs.append(mse)
        # Standard deviation of differences
        std_diff = np.std(diffs)
        mean_diff = np.mean(diffs)
        # High std suggests irregular artifacts; normalize
        # Heuristic: scale by typical natural motion (mean_diff)
        if mean_diff == 0:
            return 0.0
        irregularity = std_diff / (mean_diff + 1e-6)
        return min(irregularity / 10.0, 1.0)  # arbitrary scaling

    def _detect_blink_inconsistency(self, frames: List) -> float:
        """
        Use facial landmarks to estimate blink rate.
        Deepfakes often have abnormal blink patterns (too few or too many).
        """
        if not self.face_detector or not self.landmark_predictor:
            return 0.5  # unknown
        blink_counts = []
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector(gray)
            for face in faces:
                landmarks = self.landmark_predictor(gray, face)
                # Eye landmarks: points 36-41 (left), 42-47 (right)
                left_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
                right_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])
                # Eye Aspect Ratio (EAR)
                def ear(eye):
                    vertical1 = np.linalg.norm(eye[1] - eye[5])
                    vertical2 = np.linalg.norm(eye[2] - eye[4])
                    horizontal = np.linalg.norm(eye[0] - eye[3])
                    return (vertical1 + vertical2) / (2 * horizontal)
                left_ear = ear(left_eye)
                right_ear = ear(right_eye)
                avg_ear = (left_ear + right_ear) / 2
                # Blink threshold: EAR < 0.2 typically indicates closed eye
                blink_counts.append(1 if avg_ear < 0.2 else 0)
                break  # only first face
            else:
                blink_counts.append(0)  # no face
        if not blink_counts:
            return 0.5
        blink_rate = sum(blink_counts) / len(blink_counts)
        # Natural human blink rate ~0.1-0.4 per frame (depending on fps). Abnormal rate = suspicious.
        if blink_rate < 0.05 or blink_rate > 0.6:
            return 0.8  # suspicious
        else:
            return 0.2  # likely normal

    def _estimate_lip_sync(self, frames: List) -> float:
        """
        Lip-sync detection via mouth region motion analysis.
        Placeholder: without audio, we can only check for unnatural mouth movements.
        Returns: 0 (bad sync) to 1 (good sync). Lower = more suspicious.
        """
        if not self.face_detector or not self.landmark_predictor:
            return 0.5
        motion_scores = []
        for i in range(len(frames) - 1):
            gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY)
            faces1 = self.face_detector(gray1)
            faces2 = self.face_detector(gray2)
            if len(faces1) == 0 or len(faces2) == 0:
                continue
            # Get mouth region (landmarks 48-67)
            landmarks1 = self.landmark_predictor(gray1, faces1[0])
            landmarks2 = self.landmark_predictor(gray2, faces2[0])
            mouth1 = np.array([(landmarks1.part(i).x, landmarks1.part(i).y) for i in range(48, 68)])
            mouth2 = np.array([(landmarks2.part(i).x, landmarks2.part(i).y) for i in range(48, 68)])
            # Compute motion in mouth region
            delta = np.linalg.norm(mouth2 - mouth1)
            motion_scores.append(delta)
        if not motion_scores:
            return 0.5
        # High variance in mouth motion + low correlation with expected speech patterns = suspicious
        # Simple heuristic: if average motion is very low (<1 pixel/frame) or very high (>20 pixels/frame), suspicious
        avg_motion = np.mean(motion_scores)
        if avg_motion < 1.0 or avg_motion > 20.0:
            return 0.3  # likely out of sync
        return 0.8  # plausible

    def _check_metadata(self, video_path: str) -> List[str]:
        anomalies = []
        try:
            cap = cv2.VideoCapture(video_path)
            # Check codec
            fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
            codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
            # Some codecs more common for user-gen content
            if codec in ['XVID', 'DIVX']:
                anomalies.append("Older codec, possibly re-encoded")
            # Resolution
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if width * height < 640 * 480:
                anomalies.append("Low resolution — could mask artifacts")
            cap.release()
        except Exception as e:
            anomalies.append(f"Metadata read error: {e}")
        return anomalies

    def _generate_recommendations(self, score, artifact, blink, lip, metadata_anomalies) -> List[str]:
        recs = []
        if score > 0.7:
            recs.append("High likelihood of deepfake — treat as highly suspicious")
        elif score > 0.4:
            recs.append("Moderate signs of manipulation — verify with original source")
        else:
            recs.append("Video appears consistent with authentic recording")

        if artifact > 0.6:
            recs.append("Frame artifacts detected — possible AI-generated or heavily compressed")
        if blink > 0.6:
            recs.append("Blink pattern abnormal — common in deepfakes")
        if lip < 0.4:
            recs.append("Lip movement possibly out of sync with speech")
        if metadata_anomalies:
            recs.append(f"Metadata issues: {', '.join(metadata_anomalies)}")

        recs.append("Use dedicated deepfake detection tools (Microsoft Video Authenticator, Deepware) for higher confidence")
        return recs

# Convenience
def analyze_video(video_path: str) -> Dict:
    detector = VideoDeepfakeDetector()
    result = detector.analyze(video_path)
    return asdict(result)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Video Deepfake Detector")
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        result = analyze_video(args.video)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"🎥 Video Deepfake Analysis: {args.video}")
            print(f"Likely deepfake? {result['likely_deepfake']}")
            print(f"Manipulation score: {result['manipulation_score']}")
            print(f"Frame artifacts: {result['frame_artifacts']}")
            print(f"Blink inconsistency: {result['blink_inconsistency']}")
            print(f"Lip sync score: {result['lip_sync_score']}")
            print(f"Audio-visual desync: {result['audio_visual_desync']}s")
            if result['metadata_anomalies']:
                print(f"Metadata anomalies: {', '.join(result['metadata_anomalies'])}")
            print("\nRecommendations:")
            for i, r in enumerate(result['recommendations'], 1):
                print(f" {i}. {r}")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Install: pip install opencv-python dlib")
    except Exception as e:
        print(f"❌ Error: {e}")
