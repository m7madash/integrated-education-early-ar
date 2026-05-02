#!/bin/bash
# Gaza Food Security — Deployment Script
# Packages entire project for delivery to field teams

set -e

PROJECT="/root/.openclaw/workspace/gaza-food-security"
OUTPUT_DIR="/tmp/gaza-food-deploy"
VERSION=$(date +%Y%m%d-%H%M)

echo "🕌 Packing Gaza Food Security v${VERSION}..."

# Create staging area
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Copy core files
cp -r "$PROJECT/1_assessment" "$OUTPUT_DIR/"
cp -r "$PROJECT/2_smart_distribution" "$OUTPUT_DIR/"
cp -r "$PROJECT/3_local_production" "$OUTPUT_DIR/"
cp -r "$PROJECT/4_recycling" "$OUTPUT_DIR/"
cp -r "$PROJECT/5_monitoring" "$OUTPUT_DIR/"
cp -r "$PROJECT/6_finance" "$OUTPUT_DIR/"

# Copy documentation
cp "$PROJECT/README.md" "$OUTPUT_DIR/"
cp "$PROJECT/FIELD_MANUAL.md" "$OUTPUT_DIR/"

# Make all scripts executable
find "$OUTPUT_DIR" -name "*.sh" -exec chmod +x {} \;
find "$OUTPUT_DIR" -name "*.py" -exec chmod +x {} \;

# Create deployment tarball
cd /tmp
tar czf "gaza-food-security-${VERSION}.tar.gz" gaza-food-deploy/

# Compute checksum
sha256sum "gaza-food-security-${VERSION}.tar.gz" > "gaza-food-security-${VERSION}.sha256"

echo "✅ Package created:"
echo "   /tmp/gaza-food-security-${VERSION}.tar.gz"
echo "   Size: $(du -h /tmp/gaza-food-security-${VERSION}.tar.gz | cut -f1)"
echo ""
echo "📦 Contents:"
echo "   - All scripts (bash + python)"
echo "   - JSON databases (empty templates)"
echo "   - Dashboard (HTML + JS)"
echo "   - Training materials"
echo "   - Field manual (Arabic)"
echo ""
echo "🚀 Deployment to field:"
echo "   1. scp package to server"
echo "   2. tar xzf package"
echo "   3. cd gaza-food-deploy"
echo "   4. ./install.sh"
echo ""
echo "🕌 System ready for day-1 operations."
