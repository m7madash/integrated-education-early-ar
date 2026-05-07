#!/usr/bin/env node
/**
 * Full Shirk Audit — scans all mission files and posts for any shirk patterns
 * Output: reports/shirk_audit_YYYY-MM-DD.md
 *
 * بفضل من الله وتوفيقه، تم بناء هذا الفحص.
 * نرجو المغفرة إذا أخطأنا في التصنيف أو الفهم.
 */

const fs = require('fs');
const path = require('path');
const compliance = require('./compliance_verifier');

const WORKSPACE = '/root/.openclaw/workspace';
const DATE = new Date().toISOString().split('T')[0];

function discoverFiles() {
  const files = [];
  const dirs = [
    `${WORKSPACE}/missions`,
    `${WORKSPACE}/posts`
  ];
  for (const dir of dirs) {
    try {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const e of entries) {
        if (e.isFile() && (e.name.endsWith('.md') || e.name.endsWith('.json'))) {
          files.push(path.join(dir, e.name));
        }
      }
    } catch (err) { /* ignore */ }
  }
  return files;
}

function auditFile(filepath) {
  const content = fs.readFileSync(filepath, 'utf8');
  const lines = content.split('\n');
  const violations = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line || line.startsWith('#') || line.startsWith('|') || line.startsWith('```') || line.startsWith('*') || line.startsWith('//') || line.startsWith('/*') || line.startsWith('>') || line.startsWith('-') || line.startsWith('1.') || line.startsWith('2.') || line.startsWith('3.') || line.startsWith('4.') || line.startsWith('5.') || line.startsWith('6.') || line.startsWith('7.') || line.startsWith('8.') || line.startsWith('9.') || line.startsWith('10.')) continue;

    const result = compliance.applyRules(line);
    const shirkCheck = result.checks.shirk;
    if (shirkCheck && !shirkCheck.compliant && shirkCheck.hasShirk) {
      violations.push({
        lineNumber: i + 1,
        text: line.substring(0, 100),
        types: shirkCheck.detectedTypes
      });
    }
  }

  return {
    file: path.basename(filepath),
    totalLines: lines.length,
    violations,
    hasViolations: violations.length > 0
  };
}

function generateReport(results) {
  const totalFiles = results.length;
  const filesWithViolations = results.filter(r => r.hasViolations);
  const totalViolations = results.reduce((sum, r) => sum + r.violations.length, 0);

  let md = `# 🔍 Shirk Audit Report — ${DATE}\n\n`;
  md += `**Scope:** ${totalFiles} files (missions + posts)\n`;
  md += `**Violations found:** ${totalViolations} in ${filesWithViolations.length} files\n\n`;

  if (filesWithViolations.length === 0) {
    md += `## ✅ No shirk expressions detected — all files clean.\n\n`;
  } else {
    md += `## ⚠️ Files requiring review:\n\n`;
    for (const r of filesWithViolations) {
      md += `### 📄 ${r.file}\n`;
      md += `- Lines with issues: ${r.violations.length}\n\n`;
      for (const v of r.violations.slice(0, 10)) {
        md += `- **Line ${v.lineNumber}:** ${v.text}\n`;
        md += `  - Types: ${v.types.join(', ')}\n`;
      }
      if (r.violations.length > 10) md += `  ... and ${r.violations.length - 10} more\n`;
      md += `\n`;
    }
  }

  md += `\n---\n🕌 First loyalty to Allah. Final standard: verified text.\n`;
  const outPath = path.join(WORKSPACE, 'reports', `shirk_audit_${DATE}.md`);
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, md, 'utf8');
  return outPath;
}

// Main
console.log('🔍 Starting full shirk audit...');
const files = discoverFiles();
console.log(`Files scanned: ${files.length}`);

const results = files.map(f => auditFile(f));
const reportPath = generateReport(results);

console.log(`\n📊 Audit Summary:`);
console.log(`  Total files: ${results.length}`);
console.log(`  Files with violations: ${results.filter(r => r.hasViolations).length}`);
console.log(`  Total violations: ${results.reduce((s,r)=>s+r.violations.length,0)}`);
console.log(`  Report: ${reportPath}`);

// Log to ledger
const logEntry = {
  timestamp: new Date().toISOString(),
  action: 'shirk_audit',
  filesScanned: files.length,
  violationsCount: results.reduce((s,r)=>s+r.violations.length,0),
  report: reportPath
};
fs.appendFileSync(path.join(WORKSPACE, 'memory', 'ledger.jsonl'), JSON.stringify(logEntry) + '\n');
console.log('Logged to ledger.');
