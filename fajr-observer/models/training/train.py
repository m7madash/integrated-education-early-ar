"""
Train Dawn Classifier — Fajr Observer Agent

Uses hand-crafted optical features (from features.py) to train
a traditional ML classifier (SVM / RandomForest). No GPU needed.
Dataset structure:
  models/training/dataset/
    night/
    false_dawn/
    true_dawn/

Usage:
  python3 train.py --data models/training/dataset --model svm --output models/dawn_classifier_v1.joblib
  python3 train.py --demo --output models/dawn_classifier_demo.joblib
"""

import sys
import argparse
from pathlib import Path
import json

# Add parent to path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Conditional cv2 import: only when actually loading images
# Demo mode does NOT require OpenCV
try:
    import cv2
    import numpy as np
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False
    # Numpy is still needed for demo mode synthetic data
    try:
        import numpy as np
    except ImportError:
        print("❌ numpy is required. Install: pip install numpy")
        sys.exit(1)

from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import joblib

from src.detection.features import extract_features

def load_dataset(data_dir: Path, min_samples: int = 10):
    """Load images and extract features + labels.
    Returns (X, y, class_names). Warns if any class has fewer than min_samples."""
    if not _CV2_AVAILABLE:
        raise ImportError("OpenCV (cv2) is required to load real images. Install: pip install opencv-python-headless")

    X, y = [], []
    class_names = ["night", "false_dawn", "true_dawn"]
    class_counts = {}

    for label_idx, label in enumerate(class_names):
        class_dir = data_dir / label
        if not class_dir.exists():
            print(f"⚠️  Class directory missing: {class_dir}")
            continue
        images = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.png"))
        class_counts[label] = len(images)
        if len(images) < min_samples:
            print(f"⚠️  {label}: only {len(images)} images (recommend >= {min_samples})")
        for img_path in images:
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            feats = extract_features(img)
            X.append([feats[k] for k in sorted(feats.keys())])
            y.append(label_idx)
    if len(X) == 0:
        raise ValueError("No images loaded — check dataset folders")
    print("Dataset summary:")
    for name, count in class_counts.items():
        print(f"  {name}: {count} images")
    return np.array(X), np.array(y), class_names

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="models/training/dataset", help="Dataset directory")
    parser.add_argument("--model", choices=["svm", "rf"], default="svm", help="Classifier type")
    parser.add_argument("--output", default="models/dawn_classifier_v1.joblib", help="Output model path")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test split ratio")
    parser.add_argument("--demo", action="store_true", help="Create demo model with synthetic data (no training images required)")
    args = parser.parse_args()

    if args.demo:
        print("=== DEMO MODE: Creating synthetic model for testing ===")
        # Generate synthetic feature vectors (centroids of each class)
        # These are approximate expected feature ranges from our synthetic test images
        demo_features = {
            "night": {
                "mean_intensity": 10,
                "std_intensity": 5,
                "coverage_ratio": 0.01,
                "avg_aspect_ratio": 0.5,
                "horizontal_spread": 0.05,
                "mean_hue": 120,
                "mean_saturation": 30,
                "brightest_row_ratio": 0.8,
                "bright_pixel_count": 100
            },
            "false_dawn": {
                "mean_intensity": 60,
                "std_intensity": 20,
                "coverage_ratio": 0.15,
                "avg_aspect_ratio": 3.0,  # vertical streak
                "horizontal_spread": 0.15,
                "mean_hue": 200,
                "mean_saturation": 40,
                "brightest_row_ratio": 0.4,
                "bright_pixel_count": 5000
            },
            "true_dawn": {
                "mean_intensity": 120,
                "std_intensity": 30,
                "coverage_ratio": 0.40,
                "avg_aspect_ratio": 1.2,  # horizontal spread
                "horizontal_spread": 0.60,
                "mean_hue": 30,
                "mean_saturation": 70,
                "brightest_row_ratio": 0.2,
                "bright_pixel_count": 50000
            }
        }

        # Create synthetic samples around each centroid
        X_demo = []
        y_demo = []
        class_names = ["night", "false_dawn", "true_dawn"]
        for idx, (label, feats) in enumerate(demo_features.items()):
            # Generate 20 samples per class with small Gaussian noise
            for _ in range(20):
                sample = [
                    feats["mean_intensity"] + np.random.normal(0, 3),
                    feats["std_intensity"] + np.random.normal(0, 2),
                    feats["coverage_ratio"] + np.random.normal(0, 0.01),
                    feats["avg_aspect_ratio"] + np.random.normal(0, 0.1),
                    feats["horizontal_spread"] + np.random.normal(0, 0.02),
                    feats["mean_hue"] + np.random.normal(0, 5),
                    feats["mean_saturation"] + np.random.normal(0, 2),
                    feats["brightest_row_ratio"] + np.random.normal(0, 0.05),
                    feats["bright_pixel_count"] + np.random.normal(0, 100)
                ]
                X_demo.append(sample)
                y_demo.append(idx)

        X = np.array(X_demo)
        y = np.array(y_demo)

        # Train simple model
        if args.model == "svm":
            clf = SVC(kernel='rbf', probability=True, C=10, gamma='scale')
        else:
            clf = RandomForestClassifier(n_estimators=50, random_state=42)
        clf.fit(X, y)

        # Save
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        feature_names = sorted(demo_features["night"].keys())
        joblib.dump({
            "model": clf,
            "class_names": class_names,
            "feature_names": feature_names,
            "demo": True
        }, output_path)
        print(f"✅ Demo model saved to: {output_path}")
        print("   Note: This is a synthetic model for testing only.")
        print("   Collect real images and train with --data for production.")
        return 0

    # Regular training path (requires real images + cv2)
    if not _CV2_AVAILABLE:
        print("❌ OpenCV (cv2) is required for real image training.")
        print("   Install: pip install opencv-python-headless")
        print("   Or use --demo to create a synthetic model for testing.")
        sys.exit(1)

    data_dir = Path(args.data)
    if not data_dir.exists():
        print(f"❌ Dataset not found: {data_dir}")
        print("   Run scripts/collect_dataset.sh to create structure.")
        print("   Or use --demo to create a synthetic model for testing.")
        sys.exit(1)

    print("=== Fajr Classifier Training ===")
    X, y, class_names = load_dataset(data_dir, min_samples=10)
    if len(X) == 0:
        print("❌ No images loaded — check dataset folders")
        sys.exit(1)

    print(f"Total samples: {len(X)}")
    print(f"Features: {X.shape[1]}")
    for i, name in enumerate(class_names):
        count = np.sum(y == i)
        print(f"  {name}: {count}")

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=args.test_size, stratify=y, random_state=42)
    print(f"\nTrain: {len(X_train)}, Test: {len(X_test)}")

    # Model
    if args.model == "svm":
        clf = SVC(kernel='rbf', probability=True, C=10, gamma='scale')
    else:
        clf = RandomForestClassifier(n_estimators=100, random_state=42)

    print(f"\nTraining {args.model}...")
    clf.fit(X_train, y_train)

    # Evaluate
    acc = clf.score(X_test, y_test)
    print(f"\n✅ Test accuracy: {acc:.1%}")
    y_pred = clf.predict(X_test)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=class_names))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Save model
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    feature_names = sorted(extract_features(np.zeros((10,10,3))).keys())
    joblib.dump({
        "model": clf,
        "class_names": class_names,
        "feature_names": feature_names,
        "demo": False
    }, output_path)
    print(f"\n✅ Model saved to: {output_path}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
