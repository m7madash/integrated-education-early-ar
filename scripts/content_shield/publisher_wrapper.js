#!/usr/bin/env node

/**
 * Content Shield — Cross-Platform Publisher Wrapper (v3)
 * Used by publish scripts to filter content before sending to platforms
 */

const path = require('path');
const rootDir = path.join(__dirname, '..', '..');

// Use v3 filter with context awareness
const { filterContent } = require('./filter_v3');
const { queueForReview } = require('./review_queue');

/**
 * Publish with shield check
 */
function publishWithShield(content, platform, postId = null) {
  const isReligious = /الله|قرآن|إسلام|محمد| ﷺ|حديث|صحابة|تابعون/i.test(content);
  const result = filterContent(content, { isReligiousContent: isReligious, isPublishing: true });

  // Log decision
  const logPath = path.join(rootDir, 'reports', 'content_shield_log.jsonl');
  const logEntry = {
    timestamp: new Date().toISOString(),
    action: result.action,
    reason: result.reason,
    category: result.category || null,
    platform,
    postId,
    charCount: content.length,
    preview: content.substring(0, 100)
  };

  try {
    require('fs').appendFileSync(logPath, JSON.stringify(logEntry) + '\n');
  } catch (e) {
    console.warn('[Shield] Log write failed:', e.message);
  }

  if (result.action === 'reject') {
    return { allowed: false, action: 'reject', reason: result.reason };
  }

  if (result.action === 'flag_for_review') {
    const reviewId = queueForReview({
      content,
      category: result.category,
      reason: result.reason,
      source: platform,
      postId
    });
    return { allowed: false, action: 'queue', reviewId, reason: result.reason };
  }

  return { allowed: true, action: 'publish' };
}

// CLI
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('Usage: node publisher_wrapper.js "<content>" <platform>');
    process.exit(1);
  }
  const content = args[0];
  const platform = args[1];
  const result = publishWithShield(content, platform);
  console.log(JSON.stringify(result, null, 2));
}

module.exports = { publishWithShield };
