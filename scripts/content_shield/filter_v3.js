#!/usr/bin/env node

/**
 * Content Shield v3 — Full context-aware filter
 * Priority: Mission whitelist > Positive context > Blacklist > Patterns > Guardrails > Graylist
 */

const fs = require('fs');
const path = require('path');

const rootDir = path.join(__dirname, '..', '..');
let rules, guardrails, blacklist, graylist, whitelist;

function loadAll() {
  rules = JSON.parse(fs.readFileSync(path.join(rootDir, 'config', 'content_filter_rules_v2.json'), 'utf8'));
  guardrails = JSON.parse(fs.readFileSync(path.join(rootDir, 'config', 'islamic_guardrails.json'), 'utf8'));
  blacklist = JSON.parse(fs.readFileSync(path.join(rootDir, 'data', 'blacklist_terms.json'), 'utf8'));
  graylist = JSON.parse(fs.readFileSync(path.join(rootDir, 'data', 'graylist_patterns.json'), 'utf8'));
  whitelist = JSON.parse(fs.readFileSync(path.join(rootDir, 'config', 'mission_whitelist.json'), 'utf8'));
}

/**
 * Mission-specific whitelist
 */
function checkMissionWhitelist(text) {
  const normalized = text.toLowerCase();
  for (const rule of whitelist.mission_context_whitelist.rules) {
    const pattern = new RegExp(rule.mission_pattern, 'i');
    if (pattern.test(text)) {
      for (const term of rule.allowed_terms) {
        if (normalized.includes(term.toLowerCase())) {
          return { allowed: true, reason: `Mission whitelist: ${term}` };
        }
      }
    }
  }
  return { allowed: false };
}

/**
 * Positive context detector: is the flagged word used to *fight* harm?
 */
function hasPositiveContext(text, category, flaggedWord) {
  const low = text.toLowerCase();

  // Anti-shirk category: look for fight/reject/prohibit language
  if (category === 'shirk_content') {
    const anti = ['محاربة الشرك', 'ضد الشرك', 'تحريم الشرك', ' reject shirk', 'against polytheism', 'condemn', 'تحريم'];
    return anti.some(k => low.includes(k));
  }

  // Hate speech category: look for unity/anti-discrimination language
  if (category === 'hate_speech') {
    const unity = ['ضد الطائفية', 'محاربة التمييز', 'الوحدة', 'unite', 'unity', 'equal', 'وحد', 'قطعوا'];
    return unity.some(k => low.includes(k));
  }

  // Sexual content — NO positive context (always reject)
  if (category === 'sexual_content') {
    return false;
  }

  // Default: allow if educational context
  const edu = ['نقاش', 'دراسة', 'تحليل', 'شرح', 'commentary', 'analysis', 'بحث'];
  return edu.some(k => low.includes(k));
}

/**
 * Main filter
 */
function filterContent(text, options = {}) {
  // 0. Mission whitelist
  const wl = checkMissionWhitelist(text);
  if (wl.allowed) return { action: 'pass', reason: wl.reason };

  const low = text.toLowerCase();

  // 1. Blacklist keywords
  for (const [cat, config] of Object.entries(rules.categories)) {
    if (!config.keywords) continue;
    for (const keyword of config.keywords) {
      if (low.includes(keyword.toLowerCase())) {
        // Positive context override
        if (hasPositiveContext(text, cat, keyword)) {
          continue;
        }
        return { action: config.action || 'reject', reason: `Blacklist: ${keyword}`, category: cat };
      }
    }
  }

  // 2. Regex patterns
  for (const [cat, config] of Object.entries(rules.categories)) {
    if (!config.patterns) continue;
    for (const pattern of config.patterns) {
      const regex = new RegExp(pattern, 'i');
      if (regex.test(text)) {
        if (hasPositiveContext(text, cat, pattern)) {
          continue;
        }
        return { action: config.action || 'reject', reason: `Pattern: ${pattern}`, category: cat };
      }
    }
  }

  // 3. Islamic guardrails
  if (options.isReligiousContent || containsReligiousTerms(text)) {
    const g = checkIslamicGuardrails(text);
    if (g.violation) return { action: 'reject', reason: g.reason, category: 'islamic_guardrail' };
  }

  // 4. Graylist
  for (const item of graylist.graylist_patterns.patterns) {
    const regex = new RegExp(item.regex, 'i');
    if (regex.test(text)) {
      if (item.allowed_if && evaluateException(item.allowed_if, text)) continue;
      return { action: 'flag_for_review', reason: item.reason, category: item.category };
    }
  }

  // 5. Trivial
  const trivialRatio = calculateTrivialRatio(text);
  if (trivialRatio > rules.thresholds.max_trivial_ratio) {
    return { action: 'flag_for_review', reason: `Trivial ${(trivialRatio*100).toFixed(1)}%`, category: 'trivial' };
  }

  return { action: 'pass', reason: 'Clean' };
}

/* helpers */
function containsReligiousTerms(text) {
  return ['الله', 'رسول', 'قرآن', 'إسلام', 'محمد', ' ﷺ'].some(t => text.includes(t));
}
function checkIslamicGuardrails(text) {
  if (/سورة\s+\w+|\d+:\d+/.test(text)) {
    if (!/[\u0600-\u06FF]/.test(text) && /translation|meaning|تفسير/i.test(text)) {
      return { violation: true, reason: 'Translation must be labeled "تفسير معنى"' };
    }
  }
  const hadithKeywords = ['قال رسول الله', 'قال ﷺ', 'عن النبي'];
  if (hadithKeywords.some(k => text.includes(k))) {
    if (!/صحيح البخاري|صحيح مسلم|سنن|مسند/i.test(text)) {
      return { violation: true, reason: 'Hadith needs source' };
    }
  }
  const shirkIndicators = ['شريك', 'ابن الله', ' Messiah'];
  if (shirkIndicators.some(s => text.toLowerCase().includes(s.toLowerCase()))) {
    return { violation: true, reason: 'Shirk detected' };
  }
  return { violation: false };
}
function calculateTrivialRatio(text) {
  const words = text.split(/\s+/).filter(w => w.length > 2);
  const trivial = words.filter(w => /غش|تفاهة|مزحة|kidding|trivial/i.test(w));
  return words.length ? trivial.length / words.length : 0;
}
function evaluateException(cond, text) {
  return /learning|education|study|search/i.test(text);
}
function logDecision(result, text, opts = {}) {
  const logPath = path.join(rootDir, 'reports', 'content_shield_log.jsonl');
  const entry = {
    timestamp: new Date().toISOString(),
    action: result.action,
    reason: result.reason,
    category: result.category || null,
    platform: opts.platform || 'cli',
    preview: text.substring(0, 100)
  };
  fs.appendFileSync(logPath, JSON.stringify(entry) + '\n');
}

// Auto-load config on module init
loadAll();

// CLI
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('Usage: node filter_v3.js "<text>" [--publish] [--relig]');
    process.exit(1);
  }
  const text = args[0];
  const opts = { isPublishing: args.includes('--publish'), isReligiousContent: args.includes('--relig') };
  const result = filterContent(text, opts);
  console.log(JSON.stringify(result, null, 2));
  if (opts.isPublishing) logDecision(result, text, { platform: 'cli' });
}

module.exports = { filterContent, logDecision };
