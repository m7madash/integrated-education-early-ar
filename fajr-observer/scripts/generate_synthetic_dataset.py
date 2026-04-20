#!/usr/bin/env python3
"""
Generate synthetic dawn training images for Fajr Observer.
Uses only standard library + optional PIL (pillow).
如果PIL غير متوفر، يُنشئ ملفات metadata فقط.
"""

import argparse
from pathlib import Path
import json
import random
import math

# Try PIL; if missing, we'll generate metadata only
try:
    from PIL import Image, ImageDraw
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False
    print("⚠️  PIL (pillow) not available — will generate metadata only.")
    print("   Install for actual images: pip install pillow")

def generate_night_image(width=640, height=480, noise_level=0.02):
    """Pure black sky with faint stars (salt & pepper noise)."""
    if not _HAS_PIL:
        return None
    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Add stars
    for _ in range(int(width * height * noise_level)):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        brightness = random.randint(200, 255)
        draw.point((x, y), fill=(brightness, brightness, brightness))
    return img

def generate_false_dawn_image(width=640, height=480):
    """Vertical streak on horizon — dark sky + bright vertical column."""
    if not _HAS_PIL:
        return None
    img = Image.new("RGB", (width, height), (5, 5, 15))  # dark blue-black
    draw = ImageDraw.Draw(img)
    # Vertical streak at horizon (bottom 1/3)
    horizon_y = int(height * 0.65)
    streak_width = random.randint(8, 15)
    streak_height = int(height * 0.35)
    streak_x = random.randint(width//3, 2*width//3)
    # Gradient brightness upward
    for y in range(horizon_y, horizon_y + streak_height):
        fade = 1.0 - ((y - horizon_y) / streak_height)
        brightness = int(180 * fade + 50)
        color = (brightness, brightness, int(brightness*0.9))
        draw.rectangle([streak_x - streak_width//2, y, streak_x + streak_width//2, height-1], fill=color)
    return img

def generate_true_dawn_image(width=640, height=480):
    """Horizontal glow across entire horizon — reddish-orange gradient."""
    if not _HAS_PIL:
        return None
    img = Image.new("RGB", (width, height), (10, 10, 25))
    draw = ImageDraw.Draw(img)
    # Horizontal band at horizon
    horizon_y = random.randint(int(height*0.6), int(height*0.75))
    band_height = random.randint(30, 60)
    # Color gradient: deep red -> orange -> yellow toward top
    for y in range(horizon_y, horizon_y + band_height):
        rel = (y - horizon_y) / band_height
        r = int(255 * (1 - rel*0.3))
        g = int(200 * rel)
        b = int(150 * rel*0.5)
        draw.rectangle([0, y, width-1, y], fill=(r, g, b))
    # Additional scattered glow upward
    for y in range(0, horizon_y):
        rel = 1.0 - (y / horizon_y)
        alpha = int(200 * rel * rel)
        draw.rectangle([0, y, width-1, y], fill=(alpha, int(alpha*0.8), int(alpha*0.6)))
    return img

def generate_metadata_sample(label, index, width=640, height=480):
    """Generate a feature vector description (for metadata-only mode)."""
    if label == "night":
        base = {
            "mean_intensity": random.uniform(5, 15),
            "std_intensity": random.uniform(3, 8),
            "coverage_ratio": random.uniform(0.005, 0.02),
            "avg_aspect_ratio": random.uniform(0.3, 0.7),
            "horizontal_spread": random.uniform(0.02, 0.08),
            "mean_hue": random.uniform(100, 140),
            "mean_saturation": random.uniform(20, 40),
            "brightest_row_ratio": random.uniform(0.7, 0.9),
            "bright_pixel_count": random.randint(50, 200)
        }
    elif label == "false_dawn":
        base = {
            "mean_intensity": random.uniform(45, 75),
            "std_intensity": random.uniform(15, 25),
            "coverage_ratio": random.uniform(0.10, 0.20),
            "avg_aspect_ratio": random.uniform(2.5, 3.5),  # vertical
            "horizontal_spread": random.uniform(0.10, 0.20),
            "mean_hue": random.uniform(180, 220),
            "mean_saturation": random.uniform(30, 50),
            "brightest_row_ratio": random.uniform(0.35, 0.45),
            "bright_pixel_count": random.randint(3000, 7000)
        }
    else:  # true_dawn
        base = {
            "mean_intensity": random.uniform(100, 140),
            "std_intensity": random.uniform(25, 35),
            "coverage_ratio": random.uniform(0.35, 0.45),
            "avg_aspect_ratio": random.uniform(1.0, 1.4),  # horizontal
            "horizontal_spread": random.uniform(0.55, 0.65),
            "mean_hue": random.uniform(20, 40),
            "mean_saturation": random.uniform(60, 80),
            "brightest_row_ratio": random.uniform(0.15, 0.25),
            "bright_pixel_count": random.randint(40000, 60000)
        }
    # Add small noise to each
    return {k: v + random.normalvariate(0, v*0.05) for k, v in base.items()}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="models/training/dataset", help="Dataset directory")
    parser.add_argument("--samples", type=int, default=500, help="Samples per class")
    parser.add_argument("--no-images", action="store_true", help="Generate metadata only (requires no PIL)")
    args = parser.parse_args()

    output_dir = Path(args.output)
    classes = ["night", "false_dawn", "true_dawn"]

    print(f"=== Synthetic Fajr Dataset Generator ===")
    print(f"Output: {output_dir}")
    print(f"Samples per class: {args.samples}")
    print(f"Images: {'No (metadata only)' if args.no_images or not _HAS_PIL else 'Yes (PNG)'}")

    for cls in classes:
        class_dir = output_dir / cls
        class_dir.mkdir(parents=True, exist_ok=True)

        for i in range(args.samples):
            stem = f"{cls}_{i:04d}"
            if _HAS_PIL and not args.no_images:
                # Generate actual image
                if cls == "night":
                    img = generate_night_image()
                elif cls == "false_dawn":
                    img = generate_false_dawn_image()
                else:
                    img = generate_true_dawn_image()
                img_path = class_dir / f"{stem}.png"
                img.save(img_path, "PNG")
                # Also save metadata as JSON for reference
                meta = generate_metadata_sample(cls, i)
            else:
                # Metadata only (for training from features directly)
                meta = generate_metadata_sample(cls, i)

            meta_path = class_dir / f"{stem}.json"
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=2)

        print(f"✅ Generated {args.samples} samples: {class_dir}")

    print(f"\n✅ Dataset ready at: {output_dir}")
    print("Next: python3 models/training/train.py --data models/training/dataset --output models/dawn_classifier_v1.joblib")
    print("   Or use --demo for quick test without dataset.")

if __name__ == "__main__":
    main()
