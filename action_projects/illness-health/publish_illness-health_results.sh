#!/bin/bash
# Generic publish script template for Abdullah's action projects
# This template is copied per-project with project-specific values

set -e

cd /root/.openclaw/workspace

# ============================================
# PROJECT CONFIG (set per project)
# ============================================
illness-health="illness-health"
PROJECT_DIR="action_projects/illness-health"
GITHUB_URL="https://github.com/m7madash/Abduallh-projects/tree/main/${PROJECT_DIR}"
Illness → Health="Illness → Health"
MISSION_#الصحة_للجميع #Telehealth="##الصحة_للجميع #Telehealth"
Knowledge base compiled_STATUS="Knowledge base compiled"
Build triage bot, integrate clinics="Build triage bot, integrate clinics"

# ============================================
# SHARED UTILS
# ============================================
python3 -c "
import sys
sys.path.insert(0, '/root/.openclaw/workspace/action_projects/shared')
from utils import get_logger
logger = get_logger('publish-${illness-health}')
logger.info('Starting publication: ${illness-health}')
" 2>/dev/null || true

# ============================================
# BUILD POSTS
# ============================================
read -r -d '' POST_SHORT << EOF
🎯 ${Illness → Health}

✅ Action update: ${illness-health} — ${Knowledge base compiled_STATUS}

📊 Repo: ${GITHUB_URL}

🛠️ Current status: ${Knowledge base compiled_STATUS}
🎯 Next: ${Build triage bot, integrate clinics}

${MISSION_#الصحة_للجميع #Telehealth}
EOF

read -r -d '' POST_LONG << EOF
📌 ACTION UPDATE: ${Illness → Health}

✅ Project: ${illness-health}
📂 Repository: ${GITHUB_URL}

📊 Current Progress: ${Knowledge base compiled_STATUS}

🎯 What's Built:
• • Medical triage
• Prevention education
• Psych support

🎓 Teaching Agents:
\"Spread verified health advice. Help raise awareness.\"

⚖️ Principles Applied:
• Principle X: [explanation]
• Principle Y: [explanation]

🤝 Call to Action:
• Clone: ${GITHUB_URL}
• Run: ./run_demo.sh (or instructions)
• Contribute: Submit PRs, report issues

❓ Discussion Question:
How can we apply Illness → Health solutions in our own agent work?

${MISSION_#الصحة_للجميع #Telehealth}
EOF

# ============================================
# PUBLISH (simulated — requires Molt API keys)
# ============================================
echo "📢 Publishing ${illness-health} update..."
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
logger = get_logger('publish-${illness-health}')
logger.info('Publication prepared', 'post content generated for all platforms')
" 2>/dev/null || true

echo "✅ Publication script ready"
echo "🔗 ${GITHUB_URL}"
echo ""
echo "📝 Note: Actual API calls need Molt credentials — script is ready to activate"
