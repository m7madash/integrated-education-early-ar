#!/usr/bin/env node

/**
 * Content Shield — Filter v2.0
 * Context-aware: allows anti-shirk/anti-discrimination content
 */

const fs = require('fs');
const path = require('path');

const rootDir = path.join(__dirname, '..', '..');
let rules, guardrails, blacklist, graylist;

function loadConfig() {
  try {
    rules = JSON.parse(fs.readFileSync(path.join(rootDir, 'config', 'content_filter_rules_v2.json'), 'utf8'));
    guardrails = JSON.parse(fs.readFileSync(path.join(rootDir, 'config', 'islamic_guardrails.json'), 'utf8'));
    blacklist = JSON.parse(fs.readFileSync(path.join(rootDir, 'data', 'blacklist_terms.json'), 'utf8'));
    graylist = JSON.parse(fs.readFileSync(path.join(rootDir, 'data', 'graylist_patterns.json'), 'utf8'));
  } catch (e) {
    console.error('Content Shield v2: Config load failed:', e.message);
    process.exit(1);
  }
}

loadConfig();

/**
 * Main filter with context exceptions
 */
function filterContent(text, options = {}) {
  const normalized = text.toLowerCase();

  // --- STEP 1: Blacklist keywords (with context exceptions) ---
  for (const [category, config] of Object.entries(rules.categories)) {
    if (!config.keywords) continue;

    for (const keyword of config.keywords) {
      if (normalized.includes(keyword.toLowerCase())) {
        // Check for context exceptions BEFORE rejecting
        if (config.context_exceptions) {
          if (isAllowedByContext(text, config.context_exceptions, normalized)) {
            console.log(`[ContentShield] Keyword "${keyword}" allowed by context exception`);
            continue; // skip this keyword, keep scanning
          }
        }
        // No exception → reject/flag per category
        return {
          action: config.action || 'reject',
          reason: `Blacklist match: ${keyword}`,
          category
        };
      }
    }
  }

  // --- STEP 2: Pattern matching (regex) ---
  for (const [category, config] of Object.entries(rules.categories)) {
    if (!config.patterns) continue;
    for (const pattern of config.patterns) {
      const regex = new RegExp(pattern, 'i');
      if (regex.test(text)) {
        // Context check for patterns too
        if (config.context_exceptions && isAllowedByContext(text, config.context_exceptions, normalized)) {
          console.log(`[ContentShield] Pattern "${pattern}" allowed by context`);
          continue;
        }
        return {
          action: config.action || 'reject',
          reason: `Pattern match: ${pattern}`,
          category
        };
      }
    }
  }

  // --- STEP 3: Islamic guardrails ---
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

  // --- STEP 4: Graylist (flag for review) ---
  for (const item of graylist.graylist_patterns.patterns) {
    const regex = new RegExp(item.regex, 'i');
    if (regex.test(text)) {
      if (item.allowed_if && evaluateException(item.allowed_if, text)) {
        continue;
      }
      return {
        action: 'flag_for_review',
        reason: item.reason,
        category: item.category
      };
    }
  }

  // --- STEP 5: Trivial ratio ---
  const trivialRatio = calculateTrivialRatio(text);
  if (trivialRatio > rules.thresholds.max_trivial_ratio) {
    return {
      action: 'flag_for_review',
      reason: `Trivial content ratio ${(trivialRatio*100).toFixed(1)}%`,
      category: 'trivial_content'
    };
  }

  return { action: 'pass', reason: 'No issues detected' };
}

/**
 * Context-aware exception checker
 */
function isAllowedByContext(text, exceptions, normalized) {
  for (const exc of exceptions) {
    if (exc === 'anti_shirk_allowed') {
      // If text has anti-shirk keywords alongside shirk terms → allow
      const antiShirkKeywords = ['محاربة الشرك', 'ضد الشرك', 'تحريم الشرك', 'reject shirk', 'against polytheism', 'condemn polytheism', 'تحريم'];
      const hasAntiContext = antiShirkKeywords.some(k => text.toLowerCase().includes(k));
      if (hasAntiContext) return true;
    }
    if (exc === 'anti_discrimination_allowed') {
      const unityKeywords = ['ضد الطائفية', 'محاربة التمييز', 'الوحدة', 'unite', 'unity', 'equal', 'متساوون'];
      const hasUnityContext = unityKeywords.some(k => text.toLowerCase().includes(k));
      if (hasUnityContext) return true;
    }
    if (exc === 'religious_discussion_allowed') {
      const eduKeywords = ['نقاش', 'دراسة', 'تحليل', 'شرح', 'commentary', 'analysis', 'بحث'];
      const hasEduContext = eduKeywords.some(k => normalized.includes(k));
      if (hasEduContext) return true;
    }
  }
  return false;
}

/**
 * Existing helper functions (unchanged from v1)
 */
function containsReligiousTerms(text) {
  const religiousTerms = ['الله', 'رسول', 'قرآن', 'إسلام', 'محمد', ' ﷺ'];
  return religiousTerms.some(term => text.includes(term));
}

function checkIslamicGuardrails(text) {
  const quranSurahPattern = /سورة\s+\w+|\d+:\d+/;
  if (quranSurahPattern.test(text)) {
    const hasArabic = /[\u0600-\u06FF]/.test(text);
    const hasEnglishTranslation = /translation|meaning|تفسير/i.test(text);
    if (!hasArabic && hasEnglishTranslation) {
      return { violation: true, reason: 'Translations must be labeled "تفسير معنى"' };
    }
  }

  const hadithKeywords = ['قال رسول الله', 'قال ﷺ', 'عن النبي'];
  if (hadithKeywords.some(k => text.includes(k))) {
    const hasSource = /صحيح البخاري|صحيح مسلم|سنن|مسند/i.test(text);
    if (!hasSource) {
      return { violation: true, reason: 'Hadith requires source reference' };
    }
  }

  const shirkIndicators = ['شريك', 'ابن الله', ' Messiah', 'intermediary with God'];
  if (shirkIndicators.some(s => text.toLowerCase().includes(s.toLowerCase()))) {
    return { violation: true, reason: 'Shirk content detected — reject' };
  }

  return { violation: false };
}

function calculateTrivialRatio(text) {
  const words = text.split(/\s+/).filter(w => w.length > 2);
  const trivialWords = words.filter(w => /غش|تفاهة|مزحة|kidding|trivial/i.test(w));
  return words.length ? trivialWords.length / words.length : 0;
}

function evaluateException(condition, text) {
  if (condition.includes('context:educational')) {
    return /learning|education|study|search/i.test(text);
  }
  return false;
}

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
  const logPath = path.join(rootDir, 'reports', 'content_shield_log.jsonl');
  fs.appendFileSync(logPath, JSON.stringify(logEntry) + '\n');
}

// CLI
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('Usage: node filter_v2.js "<text>" [--publish] [--relig]');
    process.exit(1);
  }
  const text = args[0];
  const options = {
    isPublishing: args.includes('--publish'),
    isReligiousContent: args.includes('--relig')
  };
  const result = filterContent(text, options);
  console.log(JSON.stringify(result, null, 2));
  if (options.isPublishing) logDecision(result, text, { platform: 'cli' });
}

module.exports = { filterContent, logDecision };
