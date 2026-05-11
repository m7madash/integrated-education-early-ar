#!/usr/bin/env node

/**
 * Content Shield — Filter v1.0
 * Checks text against blacklist/graylist and Islamic guardrails
 * Returns: 'reject' | 'flag_for_review' | 'pass'
 */

const fs = require('fs');
const path = require('path');

// Load rules
const rootDir = path.join(__dirname, '..', '..');
const rulesPath = path.join(rootDir, 'config', 'content_filter_rules.json');
const guardrailsPath = path.join(rootDir, 'config', 'islamic_guardrails.json');
const blacklistPath = path.join(rootDir, 'data', 'blacklist_terms.json');
const graylistPath = path.join(rootDir, 'data', 'graylist_patterns.json');

let rules, guardrails, blacklist, graylist;

try {
  rules = JSON.parse(fs.readFileSync(rulesPath, 'utf8'));
  guardrails = JSON.parse(fs.readFileSync(guardrailsPath, 'utf8'));
  blacklist = JSON.parse(fs.readFileSync(blacklistPath, 'utf8'));
  graylist = JSON.parse(fs.readFileSync(graylistPath, 'utf8'));
} catch (e) {
  console.error('Content Shield: Failed to load config files:', e.message);
  process.exit(1);
}

/**
 * Main filter function
 * @param {string} text - Input text to check
 * @param {object} options - Optional flags (isReligiousContent, isPublishing, etc.)
 * @returns {object} { action: 'reject'|'flag_for_review'|'pass', reason: string, category?: string }
 */
function filterContent(text, options = {}) {
  const normalized = text.toLowerCase().trim();

  // 1. Check blacklist (auto-reject categories)
  for (const [category, config] of Object.entries(rules.categories)) {
    if (!config.keywords && !config.patterns) continue;

    // Check keywords
    for (const keyword of config.keywords || []) {
      if (normalized.includes(keyword.toLowerCase())) {
        return {
          action: config.action || 'reject',
          reason: `Blacklist match: ${keyword}`,
          category
        };
      }
    }

    // Check regex patterns
    for (const pattern of config.patterns || []) {
      const regex = new RegExp(pattern, 'i');
      if (regex.test(text)) {
        return {
          action: config.action || 'reject',
          reason: `Pattern match: ${pattern}`,
          category
        };
      }
    }
  }

  // 2. Islamic Guardrails — for religious content
  if (options.isReligiousContent || containsReligiousTerms(text)) {
    const guardrailCheck = checkIslamicGuardrails(text);
    if (guardrailCheck.violation) {
      return {
        action: 'reject',
        reason: guardrailCheck.reason,
        category: 'islamic_guardrail_violation'
      };
    }
  }

  // 3. Graylist — flag for human review
  for (const item of graylist.graylist_patterns.patterns) {
    const regex = new RegExp(item.regex, 'i');
    if (regex.test(text)) {
      // Check allowed exceptions
      if (item.allowed_if && evaluateException(item.allowed_if, text)) {
        continue;
      }
      return {
        action: 'flag_for_review',
        reason: item.reason,
        category: item.category,
        details: item
      };
    }
  }

  // 4. Additional heuristics (check for high trivial ratio, etc.)
  const trivialRatio = calculateTrivialRatio(text);
  if (trivialRatio > rules.thresholds.max_trivial_ratio) {
    return {
      action: 'flag_for_review',
      reason: `Trivial content ratio ${(trivialRatio*100).toFixed(1)}% exceeds threshold`,
      category: 'trivial_content'
    };
  }

  // Pass all checks
  return { action: 'pass', reason: 'No issues detected' };
}

/**
 * Check if text contains religious terms that trigger guardrail review
 */
function containsReligiousTerms(text) {
  const religiousTerms = ['الله', 'رسول', 'قرآن', 'إسلام', 'محمد', ' ﷺ', '伊斯Лам', ' Muslim'];
  return religiousTerms.some(term => text.includes(term));
}

/**
 * Apply Islamic guardrails to content
 */
function checkIslamicGuardrails(text) {
  // Rule 1: Quran must be Arabic only
  const quranSurahPattern = /سورة\s+\w+|\d+:\d+/;
  if (quranSurahPattern.test(text)) {
    // Check if non-Arabic translation is labeled as Quran
    const hasArabic = /[\u0600-\u06FF]/.test(text);
    const hasEnglishTranslation = /translation|meaning|تفسير/i.test(text);
    if (!hasArabic && hasEnglishTranslation) {
      return { violation: true, reason: 'Translations must be labeled "تفسير معنى"' };
    }
  }

  // Rule 2: Hadith must have source
  const hadithKeywords = ['قال رسول الله', 'قال ﷺ', 'عن النبي'];
  if (hadithKeywords.some(k => text.includes(k))) {
    const hasSource = /صحيح البخاري|صحيح مسلم|سنن|مسند/i.test(text);
    if (!hasSource) {
      return { violation: true, reason: 'Hadith requires source reference' };
    }
  }

  // Rule 3: No shirk content
  const shirkIndicators = ['شريك', 'ابن الله', ' Messiah', 'intermediary with God'];
  if (shirkIndicators.some(s => text.toLowerCase().includes(s.toLowerCase()))) {
    return { violation: true, reason: 'Shirk content detected — reject' };
  }

  return { violation: false };
}

/**
 * Calculate ratio of trivial vs meaningful words
 */
function calculateTrivialRatio(text) {
  const words = text.split(/\s+/).filter(w => w.length > 2);
  const trivialWords = words.filter(w => /غش|تفاهة|heiroglyph|مزحة| kidding/i.test(w));
  return words.length ? trivialWords.length / words.length : 0;
}

/**
 * Evaluate if exception conditions apply
 */
function evaluateException(condition, text) {
  // Simple check — can be expanded
  if (condition.includes('context:educational')) {
    return /learning|education|study|search/i.test(text);
  }
  if (condition.includes('context:medical')) {
    return /medical|health|doctor|clinical/i.test(text);
  }
  if (condition.includes('context:academic_discussion')) {
    return /analysis|critique|review|study/i.test(text);
  }
  return false;
}

/**
 * Log decision to ledger (append-only)
 */
function logDecision(result, originalText, options = {}) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    action: result.action,
    reason: result.reason,
    category: result.category || null,
    platform: options.platform || 'unknown',
    postId: options.postId || null,
    charCount: originalText.length,
    preview: originalText.substring(0, 100)
  };

  const logPath = path.join(__dirname, '..', 'reports', 'content_shield_log.jsonl');
  fs.appendFileSync(logPath, JSON.stringify(logEntry) + '\n');
}

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('Usage: node content_filter.js "<text>" [--publish] [--relig]');
    process.exit(1);
  }

  const text = args[0];
  const options = {
    isPublishing: args.includes('--publish'),
    isReligiousContent: args.includes('--relig')
  };

  const result = filterContent(text, options);
  console.log(JSON.stringify(result, null, 2));

  // Log automatically on publishing
  if (options.isPublishing) {
    logDecision(result, text, { platform: 'cli' });
  }
}

module.exports = { filterContent, logDecision };
