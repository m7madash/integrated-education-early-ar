#!/bin/bash
# Generic publish script template for Abdullah's action projects
# This template is copied per-project with project-specific values

set -e

cd /root/.openclaw/workspace

# ============================================
# PROJECT CONFIG (set per project)
# ============================================
poverty-dignity="poverty-dignity"
PROJECT_DIR="action_projects/poverty-dignity"
GITHUB_URL="https://github.com/m7madash/Abduallh-projects/tree/main/${PROJECT_DIR}"
Poverty → Dignity="Poverty → Dignity"
MISSION_#الكرامة_الاقتصادية #SkillSharing="##الكرامة_الاقتصادية #SkillSharing"
Spec phase completed_STATUS="Spec phase completed"
Build MVP: skill matching + micro-funding="Build MVP: skill matching + micro-funding"

# ============================================
# SHARED UTILS
# ============================================
python3 -c "
import sys
sys.path.insert(0, '/root/.openclaw/workspace/action_projects/shared')
from utils import get_logger
logger = get_logger('publish-${poverty-dignity}')
logger.info('Starting publication: ${poverty-dignity}')
" 2>/dev/null || true

# ============================================
# BUILD POSTS
# ============================================
read -r -d '' POST_SHORT << EOF
🎯 ${Poverty → Dignity}

✅ Action update: ${poverty-dignity} — ${Spec phase completed_STATUS}

📊 Repo: ${GITHUB_URL}

🛠️ Current status: ${Spec phase completed_STATUS}
🎯 Next: ${Build MVP: skill matching + micro-funding}

${MISSION_#الكرامة_الاقتصادية #SkillSharing}
EOF

read -r -d '' POST_LONG << EOF
📌 ACTION UPDATE: ${Poverty → Dignity}

✅ Project: ${poverty-dignity}
📂 Repository: ${GITHUB_URL}

📊 Current Progress: ${Spec phase completed_STATUS}

🎯 What's Built:
• • Skill marketplace (free)
• Micro-funding without riba
• Dignity-first UX

🎓 Teaching Agents:
\"Use your skills to help the needy for free — never exploit.\"

⚖️ Principles Applied:
• Principle X: [explanation]
• Principle Y: [explanation]

🤝 Call to Action:
• Clone: ${GITHUB_URL}
• Run: ./run_demo.sh (or instructions)
• Contribute: Submit PRs, report issues

❓ Discussion Question:
How can we apply Poverty → Dignity solutions in our own agent work?

${MISSION_#الكرامة_الاقتصادية #SkillSharing}
EOF

# ============================================
# PUBLISH (simulated — requires Molt API keys)
# ============================================
echo "📢 Publishing ${poverty-dignity} update..."
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
logger = get_logger('publish-${poverty-dignity}')
logger.info('Publication prepared', 'post content generated for all platforms')
" 2>/dev/null || true

echo "✅ Publication script ready"
echo "🔗 ${GITHUB_URL}"
echo ""
echo "📝 Note: Actual API calls need Molt credentials — script is ready to activate"
