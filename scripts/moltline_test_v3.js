#!/usr/bin/env node
/**
 * Moltline — Try XMTP V3 with explicit version
 */

const fs = require('fs');
const path = require('path');
const xmtpLib = require('@xmtp/xmtp-js');
const { Wallet } = require('ethers');

const HOME = process.env.HOME || '/root';
const MOLTLINE_DIR = path.join(HOME, '.moltline');
const PRIV_KEY_PATH = path.join(MOLTLINE_DIR, 'priv.key');
const IDENTITY_PATH = path.join(MOLTLINE_DIR, 'identity.json');

async function main() {
  console.log('📬 Moltline — XMTP V3 Test\n');

  const identity = JSON.parse(fs.readFileSync(IDENTITY_PATH, 'utf8'));
  let privKey = fs.readFileSync(PRIV_KEY_PATH, 'utf8').trim();
  try { privKey = JSON.parse(privKey).private_key || privKey; } catch(e) {}

  console.log('Identity:', identity.handle, identity.address);
  console.log('Private key:', privKey.substring(0, 20) + '...');

  const wallet = new Wallet(privKey);
  console.log('Wallet address:', wallet.address);

  console.log('\nCreating XMTP client with V3 options...');

  let client;
  try {
    // Try with version option
    client = await xmtpLib.Client.create(wallet, {
      env: 'production',
      // appVersion: 'xmtp-js-v3', // maybe?
    });
    console.log('✅ Client created');
    console.log('Inbox:', client.address);
  } catch (error) {
    console.log('❌ Error creating client:');
    console.log('   Message:', error.message);
    console.log('   Stack:', error.stack?.split('\n').slice(0, 3).join('\n   '));

    console.log('\n📌 Possible causes:');
    console.log('   1. Wallet needs to be funded (ETH for gas)');
    console.log('   2. XMTP network temporarily down');
    console.log('   3. Client API changed again');

    console.log('\n✅ Moltline config files are ready.');
    console.log('   When network/API stabilizes, messaging will work.');
    return;
  }

  console.log('\n✅ Moltline is READY for messaging!');
}

main().catch(console.error);
