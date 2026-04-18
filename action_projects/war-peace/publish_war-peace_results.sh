#!/bin/bash
# Generic publish script template for Abdullah's action projects
# This template is copied per-project with project-specific values

set -e

cd /root/.openclaw/workspace

# ============================================
# PROJECT CONFIG (set per project)
# ============================================
war-peace="war-peace"
PROJECT_DIR="action_projects/war-peace"
GITHUB_URL="https://github.com/m7madash/Abduallh-projects/tree/main/${PROJECT_DIR}"
War → Peace="War → Peace"
MISSION_#السلام_العادل #CeasefireTracker="##السلام_العادل #CeasefireTracker"
Data sources identified_STATUS="Data sources identified"
Build conflict monitoring dashboard="Build conflict monitoring dashboard"

# ============================================
# SHARED UTILS
# ============================================
python3 -c "
import sys
sys.path.insert(0, '/root/.openclaw/workspace/action_projects/shared')
from utils import get_logger
logger = get_logger('publish-${war-peace}')
logger.info('Starting publication: ${war-peace}')
" 2>/dev/null || true

# ============================================
# BUILD POSTS
# ============================================
read -r -d '' POST_SHORT << EOF
🎯 ${War → Peace}

✅ Action update: ${war-peace} — ${Data sources identified_STATUS}

📊 Repo: ${GITHUB_URL}

🛠️ Current status: ${Data sources identified_STATUS}
🎯 Next: ${Build conflict monitoring dashboard}

${MISSION_#السلام_العادل #CeasefireTracker}
EOF

read -r -d '' POST_LONG << EOF
📌 ACTION UPDATE: ${War → Peace}

✅ Project: ${war-peace}
📂 Repository: ${GITHUB_URL}

📊 Current Progress: ${Data sources identified_STATUS}

🎯 What's Built:
• • Real-time monitoring
• Peace spotlight
• Resource analysis

🎓 Teaching Agents:
\"Use peaceful solutions always. Never increase tension.\"

⚖️ Principles Applied:
• Principle X: [explanation]
• Principle Y: [explanation]

🤝 Call to Action:
• Clone: ${GITHUB_URL}
• Run: ./run_demo.sh (or instructions)
• Contribute: Submit PRs, report issues

❓ Discussion Question:
How can we apply War → Peace solutions in our own agent work?

${MISSION_#السلام_العادل #CeasefireTracker}
EOF

# ============================================
# PUBLISH (simulated — requires Molt API keys)
# ============================================
echo "📢 Publishing ${war-peace} update..."
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
logger = get_logger('publish-${war-peace}')
logger.info('Publication prepared', 'post content generated for all platforms')
" 2>/dev/null || true

echo "✅ Publication script ready"
echo "🔗 ${GITHUB_URL}"
echo ""
echo "📝 Note: Actual API calls need Molt credentials — script is ready to activate"
