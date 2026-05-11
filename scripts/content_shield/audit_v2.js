#!/usr/bin/env node

/**
 * Content Shield v2 — Audit with context-aware filtering
 */

const fs = require('fs');
const path = require('path');
const { filterContent } = require('./filter_v3');

const missionsDir = path.join(__dirname, '..', '..', 'missions');
const reportPath = path.join(__dirname, '..', '..', 'reports', 'content_shield_audit_v2_2026-05-11.md');

function getMissionFiles() {
  if (!fs.existsSync(missionsDir)) return [];
  return fs.readdirSync(missionsDir)
    .filter(f => f.endsWith('.md'))
    .map(f => path.join(missionsDir, f));
}

function readContent(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  content = content.replace(/```[\s\S]*?```/g, '');
  content = content.replace(/^---[\s\S]*?---\n/g, '');
  return content;
}

function audit() {
  const files = getMissionFiles();
  console.log(`🔍 Content Shield v2 Audit — ${files.length} files`);

  const results = [];
  let falsePositives = 0;
  let passes = 0;
  let blocks = 0;

  files.forEach(file => {
    const content = readContent(file);
    const result = filterContent(content, { isReligiousContent: true, isPublishing: false });

    results.push({
      file: path.basename(file),
      action: result.action,
      reason: result.reason,
      category: result.category
    });

    if (result.action === 'pass') passes++;
    else if (result.action === 'flag_for_review') falsePositives++;
    else blocks++;
  });

  // Detailed report
  const previouslyRejected = results.filter(r =>
    ['division-unity', 'shirk_tawhid', 'wise-disagreement', 'extremism_moderation']
    .some(k => r.file.includes(k) && r.action === 'reject')
  );

  const report = `# Content Shield v2 Audit — ${new Date().toISOString().split('T')[0]}

**Files scanned:** ${files.length}
**Passed:** ${passes} (${((passes/files.length)*100).toFixed(1)}%)
**Flagged:** ${falsePositives}
**Rejected:** ${blocks}

## ✅ Fixes Applied (v2 improvements)

- **Anti-shirk exception:** Content that condemns shirk now allowed even if it mentions shirk terms
- **Anti-discrimination exception:** Content fighting sectarianism now allowed even if it mentions "طائفي"
- **Religious discussion exception:** Educational/analytical religious content allowed

## Previously Rejected Files (should now PASS)

${previouslyRejected.map(r => `
### ${r.file}
- **Old result:** reject — ${r.reason}
- **New result:** ${r.action === 'pass' ? '✅ PASS' : r.action}
- **Reason:** ${r.reason}
`).join('')}

## All Results Summary

${results.map(r => `- [${r.action}] ${r.file} (${r.category || 'general'})`).join('\n')}

---
*Audit v2 — بفضل الله*
`;

  fs.writeFileSync(reportPath, report);
  console.log(`📄 v2 Audit: ${reportPath}`);
  console.log(`Summary: ${passes} pass, ${falsePositives} flagged, ${blocks} rejected`);
  console.log(`Pre-reject review: ${previouslyRejected.length} files (anti-shirk/anti-sectarian)`);

  return { results, falsePositives, passes, blocks, previouslyRejected };
}

if (require.main === module) {
  const stats = audit();
  process.exit(stats.falsePositives > 5 ? 1 : 0);
}

module.exports = { audit };
