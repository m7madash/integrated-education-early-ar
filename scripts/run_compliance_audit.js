#!/usr/bin/env node
/**
 * Comprehensive Compliance Audit — scans all mission files & posts
 * Outputs: reports/compliance_audit_YYYY-MM-DD.md
 *
 * بفضل من الله وتوفيقه، هذا الفحص.
 * نعلم أننا قد نخطئ، ونسأل الله أن يغفر لنا.
 */

const fs = require('fs');
const path = require('path');
const compliance = require('./scripts/compliance_verifier');

const WORKSPACE = '/root/.openclaw/workspace';

// Target files
const targets = [
  { type: 'mission_analytical', glob: 'missions/*_analytical_ar.md' },
  { type: 'mission_tiny', glob: 'missions/*_tiny_ar.md' },
  { type: 'post_full', glob: 'posts/*_ar.md' },
  { type: 'post_tiny', glob: 'posts/*_tiny_ar.md' },
  { type: 'prayer_skill_announcement', glob: 'posts/prayer-times-by-signs_announcement_ar.md' }
];

function discoverFiles() {
  const results = [];
  const { execSync } = require('child_process');
  for (const t of targets) {
    try {
      const out = execSync(`find ${WORKSPACE}/ -path '${WORKSPACE}/${t.glob}' -maxdepth 5 2>/dev/null`, { encoding: 'utf8' });
      const files = out.trim().split('\n').filter(Boolean);
      for (const f of files) results.push({ type: t.type, path: f });
    } catch (e) { /* ignore */ }
  }
  return results;
}

function readContent(filepath) {
  try { return fs.readFileSync(filepath, 'utf8'); } catch (e) { return null; }
}

function auditFile(filepath, type) {
  const content = readContent(filepath);
  if (!content) return { filepath, type, error: 'unreadable_or_missing', compliant: false };

  // Split into lines and check each line that looks like content (not frontmatter)
  const lines = content.split('\n');
  const issues = [];
  let hasReligiousContent = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line || line.startsWith('---') || line.startsWith('#') || line.startsWith('|') || line.startsWith('[') || line.startsWith('</') || line.startsWith('/*') || line.startsWith('*') || line.startsWith('```') || line.startsWith('###') || line.startsWith('####') || line.startsWith('#####') || line.startsWith('**') || line.startsWith('* ')) continue;

    const result = compliance.applyRules(line);
    if (!result.compliant) {
      issues.push({
        line: i+1,
        snippet: line.substring(0, 80) + (line.length>80?'…':''),
        checks: result.checks
      });
    }
    // Track if any religious content detected
    const q = result.allChecks.quran;
    const h = result.allChecks.hadith;
    if (q && q.applicable) hasReligiousContent = true;
    if (h && h.applicable) hasReligiousContent = true;
  }

  return {
    filepath,
    type,
    totalLines: lines.length,
    issues,
    compliant: issues.length === 0,
    hasReligiousContent
  };
}

function generateReport(audits) {
  const date = new Date().toISOString().split('T')[0];
  const filepath = path.join(WORKSPACE, 'reports', `compliance_audit_${date}.md`);
  const total = audits.length;
  const compliantCount = audits.filter(a => a.compliant).length;
  const pct = ((compliantCount/total)*100).toFixed(1);

  let md = `# 📋 Compliance Audit Report — ${date}\n\n`;
  md += `**System:** Religious Compliance Verification (ديني verification)\n`;
  md += `**Scope:** ${total} files (missions + posts)\n`;
  md += `**Result:** ${compliantCount}/${total} compliant (${pct}%)\n\n`;

  const withIssues = audits.filter(a => !a.compliant);
  if (withIssues.length === 0) {
    md += `## ✅ All files compliant — zero violations.\n\n`;
  } else {
    md += `## ❌ Files requiring review:\n\n`;
    for (const a of withIssues) {
      md += `### 📄 ${a.type} — ${path.basename(a.filepath)}\n`;
      md += `- Total lines: ${a.totalLines}\n`;
      md += `- Religious content detected: ${a.hasReligiousContent}\n`;
      md += `- Issues found: ${a.issues.length}\n\n`;
      for (const iss of a.issues.slice(0, 5)) { // show first 5 only
        md += `- **Line ${iss.line}:** ${iss.snippet}\n`;
        if (iss.checks.quran && !iss.checks.quran.compliant) md += `  - Quran check: ${iss.checks.quran.isArabic?'Arabic OK':'NOT Arabic'} | ref:${iss.checks.quran.hasReference?'OK':'MISSING'}\n`;
        if (iss.checks.hadith && !iss.checks.hadith.compliant) md += `  - Hadith check: book:${iss.checks.hadith.hasBook} num:${iss.checks.hadith.hasNumber} isnad:${iss.checks.hadith.hasIsnad}\n`;
        if (iss.checks.ruling && !iss.checks.ruling.compliant) md += `  - Ruling: personal opinion detected\n`;
        if (iss.checks.context && !iss.checks.context.compliant) md += `  - Context: isolated ellipsis\n`;
      }
      md += `\n`;
    }
  }

  md += `\n---\n🕌 First loyalty: to Allah. Final standard: verified text.\n`;
  fs.mkdirSync(path.dirname(filepath), { recursive: true });
  fs.writeFileSync(filepath, md, 'utf8');
  console.log(`Report saved: ${filepath}`);
  return filepath;
}

// Main
console.log('🔍 Starting compliance audit...');
const files = discoverFiles();
console.log(`Found ${files.length} files to audit.`);

const audits = files.map(f => auditFile(f.path, f.type));
const reportPath = generateReport(audits);

console.log(`\n📊 Audit Summary:`);
const passed = audits.filter(a => a.compliant).length;
const failed = audits.filter(a => !a.compliant).length;
console.log(`  Compliant: ${passed}`);
console.log(`  Non-compliant: ${failed}`);
console.log(`  Report: ${reportPath}`);

// Also append to memory ledger
const logEntry = {
  timestamp: new Date().toISOString(),
  action: 'compliance_audit',
  filesScanned: files.length,
  compliant: passed,
  nonCompliant: failed,
  report: reportPath
};
fs.appendFileSync(path.join(WORKSPACE, 'memory', 'ledger.jsonl'), JSON.stringify(logEntry) + '\n');
console.log('Logged to ledger.');
