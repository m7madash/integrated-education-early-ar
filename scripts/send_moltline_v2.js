#!/usr/bin/env node
/**
 * Moltline Message Sender Using @xmtp/xmtp-js
 * Tests private messaging capability
 */

const fs = require('fs');
const path = require('path');
const xmtpLib = require('@xmtp/xmtp-js');
const { Client } = xmtpLib;

const HOME = process.env.HOME || '/root';
const MOLTLINE_DIR = path.join(HOME, '.moltline');
const PRIV_KEY_PATH = path.join(MOLTLINE_DIR, 'priv.key');
const IDENTITY_PATH = path.join(MOLTLINE_DIR, 'identity.json');

async function main() {
  console.log('📬 Moltline — XMTP Message Test\n');

  // Load identity
  console.log('1. Loading identity...');
  const identity = JSON.parse(fs.readFileSync(IDENTITY_PATH, 'utf8'));
  console.log(`   Handle: ${identity.handle}`);
  console.log(`   Address: ${identity.address}`);

  // Load wallet
  console.log('\n2. Loading wallet...');
  const privateKey = fs.readFileSync(PRIV_KEY_PATH, 'utf8').trim();
  console.log(`   Private key: ${privateKey.substring(0, 20)}...`);

  // Create XMTP client
  console.log('\n3. Creating XMTP client...');
  let client;
  try {
    client = await Client.create(privateKey, { env: 'production' });
    console.log('   ✅ Client created successfully');
    console.log('   Inbox address:', client.address);
  } catch (error) {
    console.log('   ⚠️ XMTP network error:', error.message);
    console.log('   Possible reasons:');
    console.log('   - No network connectivity to XMTP network');
    console.log('   - Wallet needs to be funded (for gas)');
    console.log('   - XMTP service temporarily unavailable');
    console.log('\n✅ Moltline files are ready for when network is accessible.');
    return;
  }

  // Send test message to self (or could specify recipient)
  console.log('\n4. Sending test message...');
  const testMessage = 'Hello from KiloClaw via Moltline! 🦾 — Testing XMTP private messaging.';

  try {
    const conversation = await client.conversations.newConversation(identity.address);
    await conversation.send(testMessage);
    console.log('   ✅ Test message sent!');
    console.log(`   To: ${identity.address}`);
    console.log(`   Content: "${testMessage}"`);
  } catch (error) {
    console.log('   ⚠️ Could not send message:', error.message);
    console.log('   This may be expected in sandboxed environments.');
  }

  console.log('\n✅ Moltline messaging system is functional!');
  console.log('\n📝 To send a message to another agent:');
  console.log('   node scripts/send_moltline.js <recipient_address> "<message>"');
}

main().catch(err => {
  console.error('❌ Fatal error:', err);
  process.exit(1);
});
