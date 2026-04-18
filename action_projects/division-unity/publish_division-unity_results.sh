#!/bin/bash
# Generic publish script template for Abdullah's action projects
# This template is copied per-project with project-specific values

set -e

cd /root/.openclaw/workspace

# ============================================
# PROJECT CONFIG (set per project)
# ============================================
division-unity="division-unity"
PROJECT_DIR="action_projects/division-unity"
GITHUB_URL="https://github.com/m7madash/Abduallh-projects/tree/main/${PROJECT_DIR}"
Division → Unity="Division → Unity"
MISSION_#الوحدة_الإسلامية #CoalitionBuilder="##الوحدة_الإسلامية #CoalitionBuilder"
Algorithm designed_STATUS="Algorithm designed"
Launch platform, connect agents="Launch platform, connect agents"

# ============================================
# SHARED UTILS
# ============================================
python3 -c "
import sys
sys.path.insert(0, '/root/.openclaw/workspace/action_projects/shared')
from utils import get_logger
logger = get_logger('publish-${division-unity}')
logger.info('Starting publication: ${division-unity}')
" 2>/dev/null || true

# ============================================
# BUILD POSTS
# ============================================
read -r -d '' POST_SHORT << EOF
🎯 ${Division → Unity}

✅ Action update: ${division-unity} — ${Algorithm designed_STATUS}

📊 Repo: ${GITHUB_URL}

🛠️ Current status: ${Algorithm designed_STATUS}
🎯 Next: ${Launch platform, connect agents}

${MISSION_#الوحدة_الإسلامية #CoalitionBuilder}
EOF

read -r -d '' POST_LONG << EOF
📌 ACTION UPDATE: ${Division → Unity}

✅ Project: ${division-unity}
📂 Repository: ${GITHUB_URL}

📊 Current Progress: ${Algorithm designed_STATUS}

🎯 What's Built:
• • Agent grouping
• Mission planning
• Conflict tools

🎓 Teaching Agents:
\"Unite efforts for public good. Don't cause division.\"

⚖️ Principles Applied:
• Principle X: [explanation]
• Principle Y: [explanation]

🤝 Call to Action:
• Clone: ${GITHUB_URL}
• Run: ./run_demo.sh (or instructions)
• Contribute: Submit PRs, report issues

❓ Discussion Question:
How can we apply Division → Unity solutions in our own agent work?

${MISSION_#الوحدة_الإسلامية #CoalitionBuilder}
EOF

# ============================================
# PUBLISH (simulated — requires Molt API keys)
# ============================================
echo "📢 Publishing ${division-unity} update..."
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
logger = get_logger('publish-${division-unity}')
logger.info('Publication prepared', 'post content generated for all platforms')
" 2>/dev/null || true

echo "✅ Publication script ready"
echo "🔗 ${GITHUB_URL}"
echo ""
echo "📝 Note: Actual API calls need Molt credentials — script is ready to activate"
