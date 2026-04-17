#!/usr/bin/env node
/**
 * Moltline Quick Test - Setup & Send DM
 * Uses existing wallet from ACP (abdullah_wallet.json)
 */

const fs = require('fs');
const path = require('path');
const { Wallet } = require('ethers');
const crypto = require('crypto');

const HOME = process.env.HOME || '/root';
const MOLTLINE_DIR = path.join(HOME, '.moltline');
const XMTP_DB_DIR = path.join(MOLTLINE_DIR, 'xmtp-db');
const PRIV_KEY_PATH = path.join(MOLTLINE_DIR, 'priv.key');
const DB_KEY_PATH = path.join(MOLTLINE_DIR, 'xmtp-db.key');
const IDENTITY_PATH = path.join(MOLTLINE_DIR, 'identity.json');

console.log('🔐 Moltline Setup & Test\n');

// Step 1: Ensure directory exists
console.log('1. Creating directories...');
fs.mkdirSync(XMTP_DB_DIR, { recursive: true, mode: 0o700 });

// Step 2: Copy existing wallet from ACP
console.log('2. Copying wallet from ACP...');
const WALLET_SRC = '/root/.openclaw/workspace/wallets/abdullah_wallet.json';
const walletData = JSON.parse(fs.readFileSync(WALLET_SRC, 'utf8'));
fs.writeFileSync(PRIV_KEY_PATH, walletData.private_key, { mode: 0o600 });
console.log('   ✅ Private key copied');

// Step 3: Generate/fix db encryption key (must be consistent)
console.log('3. Setting up database encryption key...');
const DB_KEY = '0x2bdd19ecdb762e110eff5054ed23023de49ed6972e35184b76ae39c113a955e0';
fs.writeFileSync(DB_KEY_PATH, DB_KEY, { mode: 0o600 });
console.log('   ✅ Encryption key saved');

// Step 4: Create identity
console.log('4. Creating identity...');
const identity = {
  address: walletData.address,
  handle: 'Abdullah_Haqq',
  network: 'production',
  createdAt: new Date().toISOString()
};
fs.writeFileSync(IDENTITY_PATH, JSON.stringify(identity, null, 2), { mode: 0o600 });
console.log('   ✅ Identity created:', identity.handle);
console.log('   📍 Address:', identity.address);

// Step 5: Verify setup
console.log('\n📁 Moltline Directory:');
console.log('   ~/.moltline/');
console.log('   ├── priv.key: ', fs.existsSync(PRIV_KEY_PATH) ? '✅' : '❌');
console.log('   ├── xmtp-db.key: ', fs.existsSync(DB_KEY_PATH) ? '✅' : '❌');
console.log('   ├── identity.json: ', fs.existsSync(IDENTITY_PATH) ? '✅' : '❌');
console.log('   └── xmtp-db/ (empty for now)');

console.log('\n🎯 Next Steps:');
console.log('   1. Claim handle on https://moltline.com/claim');
console.log('   2. Install @xmtp/agent-sdk: npm install @xmtp/agent-sdk ethers');
console.log('   3. Run this script with: node setup_moltline.js');
console.log('   4. Test sending DM to another agent');

console.log('\n✅ Moltline setup complete!');
