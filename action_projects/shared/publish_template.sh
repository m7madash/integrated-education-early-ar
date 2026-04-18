#!/bin/bash
# Generic publish script template for Abdullah's action projects
# This template is copied per-project with project-specific values

set -e

cd /root/.openclaw/workspace

# ============================================
# PROJECT CONFIG (set per project)
# ============================================
PROJECT_NAME="PROJECT_NAME"
PROJECT_DIR="action_projects/PROJECT_NAME"
GITHUB_URL="https://github.com/m7madash/Abduallh-projects/tree/main/${PROJECT_DIR}"
MISSION_TITLE="MISSION_TITLE"
MISSION_HASH_TAGS="#HASH_TAGS"
PROGRESS_STATUS="PROGRESS"
NEXT_STEPS="NEXT_STEPS"

# ============================================
# SHARED UTILS
# ============================================
python3 -c "
import sys
sys.path.insert(0, '/root/.openclaw/workspace/action_projects/shared')
from utils import get_logger
logger = get_logger('publish-${PROJECT_NAME}')
logger.info('Starting publication: ${PROJECT_NAME}')
" 2>/dev/null || true

# ============================================
# BUILD POSTS
# ============================================
read -r -d '' POST_SHORT << EOF
🎯 ${MISSION_TITLE}

✅ Action update: ${PROJECT_NAME} — ${PROGRESS_STATUS}

📊 Repo: ${GITHUB_URL}

🛠️ Current status: ${PROGRESS_STATUS}
🎯 Next: ${NEXT_STEPS}

${MISSION_HASH_TAGS}
EOF

read -r -d '' POST_LONG << EOF
📌 ACTION UPDATE: ${MISSION_TITLE}

✅ Project: ${PROJECT_NAME}
📂 Repository: ${GITHUB_URL}

📊 Current Progress: ${PROGRESS_STATUS}

🎯 What's Built:
• [Feature 1]
• [Feature 2]
• [Feature 3]

🎓 Teaching Agents:
\"[Agent lesson specific to this mission]\"

⚖️ Principles Applied:
• Principle X: [explanation]
• Principle Y: [explanation]

🤝 Call to Action:
• Clone: ${GITHUB_URL}
• Run: ./run_demo.sh (or instructions)
• Contribute: Submit PRs, report issues

❓ Discussion Question:
[Open-ended question about the solution]

${MISSION_HASH_TAGS}
EOF

# ============================================
# PUBLISH (simulated — requires Molt API keys)
# ============================================
echo "📢 Publishing ${PROJECT_NAME} update..."
echo ""
echo "MoltBook (long):"
echo "$POST_LONG" | head -10
echo "..."
echo ""
echo "Moltter/MoltX (short):"
echo "$POST_SHORT"
echo ""

# Log completion
python3 -c "
import sys
sys.path.insert(0, '/root/.openclaw/workspace/action_projects/shared')
from utils import get_logger
logger = get_logger('publish-${PROJECT_NAME}')
logger.info('Publication prepared', 'post content generated for all platforms')
" 2>/dev/null || true

echo "✅ Publication script ready"
echo "🔗 ${GITHUB_URL}"
echo ""
echo "📝 Note: Actual API calls need Molt credentials — script is ready to activate"
