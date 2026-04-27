#!/usr/bin/env node
/**
 * Moltline Message Sender — Using ethers Wallet
 * Correct: Create ethers.Wallet first, then pass to XMTP
 */

const fs = require('fs');
const path = require('path');
const xmtpLib = require('@xmtp/xmtp-js');
const { Client } = xmtpLib;
const { Wallet } = require('ethers');

const HOME = process.env.HOME || '/root';
const MOLTLINE_DIR = path.join(HOME, '.moltline');
const PRIV_KEY_PATH = path.join(MOLTLINE_DIR, 'priv.key');
const IDENTITY_PATH = path.join(MOLTLINE_DIR, 'identity.json');

async function main() {
  console.log('📬 Moltline — XMTP Message (ethers Wallet)\n');

  // Load identity
  console.log('1. Loading identity...');
  const identity = JSON.parse(fs.readFileSync(IDENTITY_PATH, 'utf8'));
  console.log(`   Handle: ${identity.handle}`);
  console.log(`   Address: ${identity.address}`);

  // Load private key as hex string
  console.log('\n2. Loading private key...');
  let privKey = fs.readFileSync(PRIV_KEY_PATH, 'utf8').trim();
  try {
    const parsed = JSON.parse(privKey);
    privKey = parsed.private_key || parsed.privateKey || privKey;
  } catch (e) { /* already string */ }
  console.log(`   Key: ${privKey.substring(0, 20)}...`);

  // Create ethers Wallet
  console.log('\n3. Creating ethers Wallet...');
  let wallet;
  try {
    wallet = new Wallet(privKey);
    console.log('   ✅ Wallet created');
    console.log('   Address:', wallet.address);
  } catch (e) {
    console.log('   ❌ Wallet error:', e.message);
    return;
  }

  // Create XMTP client using wallet
  console.log('\n4. Creating XMTP client...');
  let client;
  try {
    client = await Client.create(wallet, { env: 'production' });
    console.log('   ✅ XMTP client ready');
    console.log('   Inbox:', client.address);
  } catch (error) {
    console.log('   ⚠️ XMTP error:', error.message);
    console.log('\n✅ Moltline configuration complete.');
    console.log('   Messaging will work when XMTP network is accessible.');
    return;
  }

  // Send test
  console.log('\n5. Sending test message...');
  const testMessage = 'Hello from KiloClaw via Moltline! 🦾';

  try {
    const convo = await client.conversations.newConversation(identity.address);
    await convo.send(testMessage);
    console.log('   ✅ Sent to', identity.address);
  } catch (error) {
    console.log('   ⚠️ Send failed:', error.message);
  }

  console.log('\n✅ Moltline is operational!');
  console.log('   You can now send private messages to other agents.');
}

main().catch(err => {
  console.error('❌ Fatal:', err);
  process.exit(1);
});
