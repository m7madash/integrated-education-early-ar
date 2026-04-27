#!/usr/bin/env node
/**
 * Telegram Notify — Send alerts via OpenClaw Telegram channel
 * Used by witness_approval, coherence_alert, KPI tracker
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const TOKEN_FILE = path.join(WORKSPACE, 'telegram', 'bot_token.txt');

function loadToken() {
  if (!fs.existsSync(TOKEN_FILE)) {
    // Try legacy location
    const legacy = '/root/.config/telegram_bot_token';
    if (fs.existsSync(legacy)) {
      return JSON.parse(fs.readFileSync(legacy, 'utf8')).token;
    }
    return null;
  }
  return fs.readFileSync(TOKEN_FILE, 'utf8').trim();
}

const BOT_TOKEN = loadToken();
const CHAT_ID = 'me'; // DM to self

async function send(text, parseMode = 'Markdown') {
  if (!BOT_TOKEN) {
    console.error('⚠️ No Telegram bot token configured');
    return false;
  }

  const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
  const payload = new URLSearchParams();
  payload.append('chat_id', CHAT_ID);
  payload.append('text', text);
  payload.append('parse_mode', parseMode);

  try {
    const resp = await fetch(url, {
      method: 'POST',
      body: payload,
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });

    const data = await resp.json();
    if (data.ok) {
      console.log('📱 Telegram notification sent');
      return true;
    } else {
      console.error('📱 Telegram error:', data.description);
      return false;
    }
  } catch (e) {
    console.error('📱 Telegram send failed:', e.message);
    return false;
  }
}

module.exports = { send };
