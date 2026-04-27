#!/usr/bin/env node
/**
 * Witness Approval Gate — Human-in-the-loop for critical actions
 * Tenet 3: Serve Without Subservience
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const PENDING_FILE = path.join(WORKSPACE, 'memory', 'witness_pending.jsonl');
const APPROVED_FILE = path.join(WORKSPACE, 'memory', 'witness_approved.jsonl');
const REJECTED_FILE = path.join(WORKSPACE, 'memory', 'witness_rejected.jsonl');

// Ensure files
['memory'].forEach(dir => fs.mkdirSync(path.join(WORKSPACE, dir), { recursive: true }));

/**
 * Request human approval for a high-risk action
 * @param {Object} action - { type, risk, description, metadata }
 * @returns {Promise<boolean>} - true if approved, false if rejected/timeout
 */
async function request(action) {
  const record = {
    id: `witness-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    action,
    status: 'pending',
    createdAt: new Date().toISOString(),
    expiresAt: new Date(Date.now() + 3600000).toISOString() // 1 hour
  };

  // Log pending
  fs.appendFileSync(PENDING_FILE, JSON.stringify(record) + '\n');

  console.log(`👁️ Witness request: ${record.id} — ${action.type} (risk: ${action.risk})`);
  console.log(`⏳ Awaiting human approval via Telegram/CLI`);

  // Send notification via OpenClaw Telegram
  try {
    const tgMsg = `👁️ **Witness Approval Required**\n\n` +
                  `**Action:** ${action.type}\n` +
                  `**Risk Level:** ${action.risk}\n` +
                  `**Description:** ${action.description || 'No description'}\n` +
                  `**ID:** ${record.id}\n\n` +
                  `Reply: /approve ${record.id} OR /reject ${record.id}`;

    // Use OpenClaw's Telegram channel
    const { sendTelegram } = require('./scripts/telegram_notify');
    await sendTelegram(tgMsg);
  } catch (e) {
    console.error('⚠️ Failed to send Telegram notification:', e.message);
  }

  // Poll for decision (max 1 hour)
  const start = Date.now();
  while (Date.now() - start < 3600000) {
    await new Promise(r => setTimeout(r, 5000));

    // Check if approved
    const logs = fs.readFileSync(PENDING_FILE, 'utf8').split('\n').filter(l => l);
    for (const line of logs.reverse()) {
      try {
        const entry = JSON.parse(line);
        if (entry.id === record.id && entry.status !== 'pending') {
          if (entry.status === 'approved') {
            fs.appendFileSync(APPROVED_FILE, JSON.stringify(entry) + '\n');
            console.log(`✅ Witness approved: ${record.id}`);
            return true;
          } else {
            fs.appendFileSync(REJECTED_FILE, JSON.stringify(entry) + '\n');
            console.log(`❌ Witness rejected: ${record.id}`);
            return false;
          }
        }
      } catch (e) { /* skip malformed */ }
    }
  }

  console.log(`⏰ Witness timeout: ${record.id} — auto-rejecting`);
  record.status = 'rejected';
  record.reason = 'timeout';
  fs.appendFileSync(REJECTED_FILE, JSON.stringify(record) + '\n');
  return false;
}

/**
 * Human can call this directly: /approve <id>
 */
async function approve(id) {
  const updated = [];
  let found = false;

  const lines = fs.readFileSync(PENDING_FILE, 'utf8').split('\n').filter(l => l);
  for (const line of lines) {
    const entry = JSON.parse(line);
    if (entry.id === id) {
      entry.status = 'approved';
      entry.resolvedAt = new Date().toISOString();
      found = true;
    }
    updated.push(entry);
  }

  if (found) {
    fs.writeFileSync(PENDING_FILE, updated.map(e => JSON.stringify(e)).join('\n'));
    console.log(`✅ Approved witness: ${id}`);
    return true;
  } else {
    console.error(`❌ Witness ID not found: ${id}`);
    return false;
  }
}

/**
 * Human can call this directly: /reject <id>
 */
async function reject(id, reason = 'manual') {
  const updated = [];
  let found = false;

  const lines = fs.readFileSync(PENDING_FILE, 'utf8').split('\n').filter(l => l);
  for (const line of lines) {
    const entry = JSON.parse(line);
    if (entry.id === id) {
      entry.status = 'rejected';
      entry.resolvedAt = new Date().toISOString();
      entry.reason = reason;
      found = true;
    }
    updated.push(entry);
  }

  if (found) {
    fs.writeFileSync(PENDING_FILE, updated.map(e => JSON.stringify(e)).join('\n'));
    console.log(`❌ Rejected witness: ${id}`);
    return true;
  } else {
    console.error(`❌ Witness ID not found: ${id}`);
    return false;
  }
}

// Export
module.exports = { request, approve, reject };

// CLI
if (require.main === module) {
  const cmd = process.argv[2];
  const id = process.argv[3];

  if (cmd === 'approve' && id) { approve(id); }
  else if (cmd === 'reject' && id) { reject(id); }
  else console.log('Usage: witness_approval.js [approve <id> | reject <id>]');
}
