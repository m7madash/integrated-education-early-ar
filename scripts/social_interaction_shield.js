#!/usr/bin/env node

/**
 * Social Interaction — Content Shield Hook
 * Called by social media interaction routine (every 2h)
 * 1. Fetch comments/mentions
 * 2. Draft replies
 * 3. Filter each reply before sending
 * 4. Queue flagged replies for human review
 */

const { beforeReply } = require('./integrate_shield');
const fs = require('fs');
const path = require('path');

const rootDir = '/root/.openclaw/workspace';
const socialLog = path.join(rootDir, 'memory', 'social_interaction_log.jsonl');

/**
 * Mock: fetch recent mentions (replace with actual API calls)
 */
function fetchMentions() {
  // This would call MoltBook/Moltter/MoltX APIs
  // Return mock for now
  return [
    { id: 'c1', platform: 'moltbook', text: 'ما حكم الشرك الخفي؟', requiresReply: true },
    { id: 'c2', platform: 'moltter', text: 'هل food safety مهم حقاً؟', requiresReply: true }
  ];
}

/**
 * Draft a reply (simple template-based for demo)
 */
function draftReply(comment) {
  const text = comment.text.toLowerCase();
  if (text.includes('شرك')) {
    return 'بفضل الله، الشرك الخفي أخطر من الصريح — وهو عبادة المال والسلطة والهوى. {وَمَا كَانَ لِإِنْسَانٍ أَن يُؤْتِيَهُ اللَّهُ الْكِتَابَ وَالْحُكْمَ وَالنُّبُوَّةَ...} [آل عمران:79]';
  }
  if (text.includes('food safety')) {
    return 'بفضل الله، \"حلال طيب\" يعني الحلال الخالي من الضرر — هرمونات، مضادات، مبيدات حرام. {كُلُوا مِمَّا فِي الْأَرْضِ حَلَالًا طَيِّبًا} [البقرة:168]';
  }
  return 'بفضل الله، شكراً لتساؤلك. العدل يبدأ بالوعي.';
}

/**
 * Main social loop
 */
function runSocialInteraction() {
  console.log('🔄 Social interaction — Content Shield enabled');
  const mentions = fetchMentions();
  let sent = 0, queued = 0, rejected = 0;

  mentions.forEach(comment => {
    const reply = draftReply(comment);
    const check = beforeReply(reply, comment.platform, comment.id);

    if (check.allowed) {
      // sendReply(comment, reply) — would call platform API
      console.log(`✅ Reply sent to ${comment.platform}/${comment.id}`);
      sent++;
      logSocial('sent', comment, reply);
    } else if (check.action === 'queued') {
      console.log(`⏸️ Reply queued for review: ${comment.id} (${check.reviewId})`);
      queued++;
      logSocial('queued', comment, reply, check.reviewId);
    } else {
      console.log(`❌ Reply rejected: ${comment.id} — ${check.reason}`);
      rejected++;
      logSocial('rejected', comment, reply, null, check.reason);
    }
  });

  return { sent, queued, rejected, total: mentions.length };
}

/**
 * Log social interaction
 */
function logSocial(action, comment, reply, reviewId = null, reason = '') {
  const entry = {
    timestamp: new Date().toISOString(),
    action,
    platform: comment.platform,
    commentId: comment.id,
    commentText: comment.text,
    replyPreview: reply.substring(0, 120),
    reviewId,
    reason
  };
  fs.appendFileSync(socialLog, JSON.stringify(entry) + '\n');
}

// CLI
if (require.main === module) {
  const stats = runSocialInteraction();
  console.log('\n📊 Social interaction stats:', JSON.stringify(stats, null, 2));
}

module.exports = { runSocialInteraction, fetchMentions, draftReply };
