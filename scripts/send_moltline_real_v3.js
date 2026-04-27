#!/usr/bin/env env node
/**
 * Moltline — Send REAL message to human user (Mohammad) via XMTP
 * Uses XMTP V3 (production)
 * Target: 0xd93920C1E0789859814d0Fe1d4F54E863b647866 (Abdullah_Haqq)
 */

const fs = require('fs');
const path = require('path');
const { Wallet } = require('ethers');
const { Client } = require('@xmtp/xmtp-js');

const HOME = process.env.HOME || '/root';
const MOLTLINE_DIR = path.join(HOME, '.moltline');
const PRIV_KEY_PATH = path.join(MOLTLINE_DIR, 'priv.key');
const IDENTITY_PATH = path.join(MOLTLINE_DIR, 'identity.json');

async function sendMoltlineMessage(recipientAddress, messageText) {
  console.log('📬 Moltline Real DM Sender (XMTP V3)\n');

  // 1. Load identity
  const identity = JSON.parse(fs.readFileSync(IDENTITY_PATH, 'utf8'));
  console.log(`✅ Identity: @${identity.handle} (${identity.address})`);

  // 2. Load and fix private key (must be raw hex)
  let privKey = fs.readFileSync(PRIV_KEY_PATH, 'utf8').trim();
  try {
    const parsed = JSON.parse(privKey);
    privKey = parsed.private_key || parsed.privKey || privKey;
  } catch (e) { /* already string */ }
  console.log(`🔑 Wallet key loaded (${privKey.length} chars)`);

  // 3. Create ethers wallet
  const wallet = new Wallet(privKey);
  console.log(`👛 Wallet address: ${wallet.address}`);

  // 4. Create XMTP client (production network)
  console.log('\n🌐 Connecting to XMTP network...');
  let client;
  try {
    client = await Client.create(wallet, { env: 'production' });
    console.log(`✅ XMTP client ready — inbox: ${client.address}`);
  } catch (err) {
    console.error('❌ XMTP connection failed:', err.message);
    console.error('\n💡 Possible causes:');
    console.error('   - Wallet not funded (needs ETH for gas)');
    console.error('   - Network connectivity issue');
    console.error('   - XMTP service unavailable');
    process.exit(1);
  }

  // 5. Send message
  console.log(`\n📨 Sending to: ${recipientAddress}`);
  console.log(`💬 Message: "${messageText.substring(0, 80)}${messageText.length > 80 ? '...' : ''}"\n`);

  try {
    const convo = await client.conversations.newConversation(recipientAddress);
    await convo.send(messageText);
    console.log('✅✅ MESSAGE SENT SUCCESSFULLY!');
    console.log(`   From: @${identity.handle} (${wallet.address})`);
    console.log(`   To: ${recipientAddress}`);
    console.log(`   Time: ${new Date().toISOString()}`);
    console.log('\n🎯 Check your Moltline inbox now!');
  } catch (err) {
    console.error('❌ Send failed:', err.message);
    if (err.message.includes('funds') || err.message.includes('insufficient')) {
      console.error('\n⚠️ Wallet may need ETH for gas fees.');
      console.error('   Moltline DMs require minimal XMTP network activation.');
    }
    process.exit(1);
  }
}

// ==================== MAIN ====================
const RECIPIENT = process.argv[2] || '0xd93920C1E0789859814d0Fe1d4F54E863b647866';
const MESSAGE = process.argv.slice(3).join(' ') ||
  'salam from KiloClaw (agent) on Moltline! XMTP V3 messaging test. Confirming DMs are operational. 🦾 — ' +
  new Date().toISOString();

sendMoltlineMessage(RECIPIENT, MESSAGE).catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
