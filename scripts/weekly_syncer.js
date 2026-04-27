#!/usr/bin/env node
/**
 * Weekly Syncer — Abdullah projects & m7mad-ai-work coordination
 * Continuity-improvement item #6: Project sync mechanism
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const WORKSPACE = '/root/.openclaw/workspace';
const SYNC_LOG = `${WORKSPACE}/logs/project_sync_$(new Date().toISOString().split('T')[0]).log`;
const SYNC_MANIFEST = `${WORKSPACE}/sync_manifest.json`;

function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}`;
  console.log(line);
  fs.appendFileSync(SYNC_LOG, line + '\n');
}

/**
 * Scan both repos for shared dependencies, overlapping work, gaps
 */
async function syncRepos() {
  log("🔍 Starting weekly project sync...");

  const repos = {
    'Abdullah_projects': '/root/.openclaw/workspace', // main workspace
    'm7mad-ai-work': '/root/m7mad-ai-work' // assumed path
  };

  // Check if m7mad-ai-work exists
  if (!fs.existsSync(repos.m7mad_ai_work)) {
    log("⚠️ m7mad-ai-work repo not found at /root/m7mad-ai-work — skipping remote sync");
    repos.m7mad_ai_work = null;
  }

  const manifest = {
    timestamp: Date.now(),
    date: new Date().toISOString().split('T')[0],
    scans: {}
  };

  // Scan workspace for missions, action_projects, skills
  const scanDir = (dir) => {
    const missions = [];
    const actionProjects = [];
    const skills = [];

    try {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        if (entry.isDirectory()) {
          if (entry.name.startsWith('mission-') || entry.name.startsWith('division-unity')) {
            missions.push(entry.name);
          } else if (entry.name === 'action_projects') {
            const apPath = path.join(dir, 'action_projects');
            try {
              const apDirs = fs.readdirSync(apPath, { withFileTypes: true });
              for (const ap of apDirs) {
                if (ap.isDirectory()) {
                  actionProjects.push(ap.name);
                }
              }
            } catch (e) {}
          } else if (entry.name === 'skills') {
            skills.push(entry.name);
          }
        }
      }
    } catch (e) {
      log(`⚠️ Scan error in ${dir}: ${e.message}`);
    }

    return { missions, actionProjects, skills };
  };

  // Scan main workspace
  const mainScan = scanDir(WORKSPACE);
  manifest.scans['Abdullah_projects'] = mainScan;
  log(`✅ Scanned Abdullah_projects: ${mainScan.missions.length} missions, ${mainScan.actionProjects.length} actionProjects`);

  // Scan m7mad-ai-work if exists
  if (repos.m7mad_ai_work) {
    const remoteScan = scanDir(repos.m7mad_ai_work);
    manifest.scans['m7mad_ai_work'] = remoteScan;
    log(`✅ Scanned m7mad_ai-work: ${remoteScan.missions.length} missions, ${remoteScan.actionProjects.length} actionProjects`);

    // Identify overlaps and gaps
    const overlapMissions = mainScan.missions.filter(m => remoteScan.missions.includes(m));
    const uniqueToMain = mainScan.missions.filter(m => !remoteScan.missions.includes(m));
    const uniqueToRemote = remoteScan.missions.filter(m => !mainScan.missions.includes(m));

    log("\n📊 Overlap Analysis:");
    log(`  Shared missions: ${overlapMissions.join(', ') || 'none'}`);
    log(`  Unique to main: ${uniqueToMain.join(', ') || 'none'}`);
    log(`  Unique to remote: ${uniqueToRemote.join(', ') || 'none'}`);

    // Action items
    manifest.recommendations = [];
    if (uniqueToMain.length > 0) {
      manifest.recommendations.push(`Sync: push ${uniqueToMain.length} missions to remote`);
    }
    if (uniqueToRemote.length > 0) {
      manifest.recommendations.push(`Sync: pull ${uniqueToRemote.length} missions from remote`);
    }
    if (overlapMissions.length === 0) {
      manifest.recommendations.push("⚠️ No shared missions — consider consolidation");
    }
  } else {
    log("ℹ️ No remote repo — standalone mode");
  }

  // Write manifest
  fs.writeFileSync(SYNC_MANIFEST, JSON.stringify(manifest, null, 2));
  log(`📝 Sync manifest written: ${SYNC_MANIFEST}`);

  // Generate report
  const reportPath = `${WORKSPACE}/reports/sync_${manifest.date}.md`;
  fs.mkdirSync(path.dirname(reportPath), { recursive: true });
  fs.writeFileSync(reportPath, generateReport(manifest));

  log(`📄 Report generated: ${reportPath}`);
  log("✅ Weekly sync complete");
}

function generateReport(manifest) {
  return `# Weekly Project Sync — ${manifest.date}

## 📊 Scan Summary

### Abdullah_projects (main workspace)
- Missions: ${manifest.scans.Abdullah_projects.missions.length}
- Action Projects: ${manifest.scans.Abdullah_projects.actionProjects.length}

${manifest.scans.m7mad_ai_work ? `### m7mad-ai-work (remote)
- Missions: ${manifest.scans.m7mad_ai_work.missions.length}
- Action Projects: ${manifest.scans.m7mad_ai_work.actionProjects.length}
` : ''}

## 🔗 Overlap Analysis

${manifest.recommendations ? manifest.recommendations.join('\n') : 'No issues detected — projects are in sync.'}

## 📝 Action Items

1. Review manifest: \`cat ${SYNC_MANIFEST}\`
2. Resolve any duplicate work
3. Update shared dependencies list
4. Commit sync report to both repos

---
*Generated by weekly-syncer.js — Continuity Infrastructure v2.0*
`;
}

// Run
syncRepos().catch(err => {
  log(`❌ Sync failed: ${err.message}`);
  process.exit(1);
});
