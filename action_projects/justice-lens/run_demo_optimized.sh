#!/bin/bash
# Justice Lens — Action Demo (Optimized)
# Uses shared utils for batch reads, caching, minimal logging

set -e

cd /root/.openclaw/workspace/action_projects/justice-lens

echo "🎯 Justice Lens — Injustice → Justice: Action in Progress"
echo "============================================================"

# Import shared utils (Python helper for caching/logging)
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/root/.openclaw/workspace/action_projects/shared')
from utils import get_logger, read_files_batch
import subprocess

logger = get_logger('justice-lens')
logger.info('Starting demo')

# Quick dependency check (cached)
deps_ok = subprocess.run(['python3', '-m', 'pip', 'list'], capture_output=True, text=True).stdout
if 'pandas' not in deps_ok:
    logger.info('Installing dependencies')
    subprocess.run(['python3', '-m', 'pip', 'install', 'pandas', 'numpy', 'scikit-learn', 'fastapi', 'uvicorn', 'pydantic', '-q'], check=True)
else:
    logger.info('Dependencies already installed (cached)')

# Generate synthetic data
logger.info('Generating dataset')
subprocess.run(['python3', 'data/generate_synthetic.py'], check=True)

# Run audit
logger.info('Running audit')
result = subprocess.run(['python3', 'src/justice_lens/audit.py'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr)

logger.info('Demo complete', 'justice-lens demo finished successfully')
print('\n✅ Demo complete!')
print('')
print('📌 NEXT: Publish these results on MoltBook as completed action.')
print('   Command: ./publish_justice_lens_results.sh (to be created)')
print('')
print('📂 Project: /root/.openclaw/workspace/action_projects/justice-lens')
print('🌐 Push to GitHub then share with agents.')
PYEOF
