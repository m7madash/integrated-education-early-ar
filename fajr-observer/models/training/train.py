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
"""

import sys
import argparse
from pathlib import Path
import json

# Add parent to path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import cv2
import numpy as np
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import joblib

from src.detection.features import extract_features

def load_dataset(data_dir: Path):
    """Load images and extract features + labels."""
    X, y = [], []
    class_names = ["night", "false_dawn", "true_dawn"]
    for label_idx, label in enumerate(class_names):
        class_dir = data_dir / label
        if not class_dir.exists():
            print(f"⚠️  Class dir missing: {class_dir}")
            continue
        images = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.png"))
        print(f"Loading {len(images)} images from '{label}'...")
        for img_path in images:
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            feats = extract_features(img)
            X.append([feats[k] for k in sorted(feats.keys())])
            y.append(label_idx)
    return np.array(X), np.array(y), class_names

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="models/training/dataset", help="Dataset directory")
    parser.add_argument("--model", choices=["svm", "rf"], default="svm", help="Classifier type")
    parser.add_argument("--output", default="models/dawn_classifier_v1.joblib", help="Output model path")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test split ratio")
    args = parser.parse_args()

    data_dir = Path(args.data)
    if not data_dir.exists():
        print(f"❌ Dataset not found: {data_dir}")
        print("   Run scripts/collect_dataset.sh to create structure, then add images.")
        sys.exit(1)

    print("=== Fajr Classifier Training ===")
    X, y, class_names = load_dataset(data_dir)
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
    joblib.dump({"model": clf, "class_names": class_names, "feature_names": sorted(extract_features(np.zeros((10,10,3))).keys())}, output_path)
    print(f"\n✅ Model saved to: {output_path}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
