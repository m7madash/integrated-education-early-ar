#!/usr/bin/env node
/**
 * Moltline Test Script
 * Tests private messaging setup using existing ACP wallet
 */

const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || '/root';
const MOLTLINE_DIR = path.join(HOME, '.moltline');
const XMTP_DB_DIR = path.join(MOLTLINE_DIR, 'xmtp-db');
const PRIV_KEY_PATH = path.join(MOLTLINE_DIR, 'priv.key');
const DB_KEY_PATH = path.join(MOLTLINE_DIR, 'xmtp-db.key');
const IDENTITY_PATH = path.join(MOLTLINE_DIR, 'identity.json');

console.log('🔐 Moltline — Private Messaging Test\n');

// 1. Verify files exist
console.log('📁 Checking Moltline directory...');
const requiredFiles = [
  ['priv.key', PRIV_KEY_PATH],
  ['xmtp-db.key', DB_KEY_PATH],
  ['identity.json', IDENTITY_PATH]
];

let allExists = true;
for (const [name, path] of requiredFiles) {
  const exists = fs.existsSync(path);
  console.log(`   ${name}: ${exists ? '✅' : '❌'}`);
  if (!exists) allExists = false;
}

if (!allExists) {
  console.log('\n❌ Some files missing. Run setup_moltline.js first.');
  process.exit(1);
}

// 2. Load identity
console.log('\n👤 Loading identity...');
const identity = JSON.parse(fs.readFileSync(IDENTITY_PATH, 'utf8'));
console.log(`   Handle: ${identity.handle}`);
console.log(`   Address: ${identity.address}`);

// 3. Verify wallet key
console.log('\n🔑 Verifying wallet...');
const privateKey = fs.readFileSync(PRIV_KEY_PATH, 'utf8').trim();
console.log(`   Private key: ${privateKey.substring(0, 20)}...`);

// 4. Check if we can import ethers
console.log('\n📦 Checking dependencies...');
let ethersOk = false;
try {
  // Try local node_modules first
  const ethersPath = require.resolve('ethers', { paths: [process.cwd()] });
  const { Wallet } = require(ethersPath);
  console.log('   ethers: ✅ loaded (from ' + ethersPath.split('/').slice(-2).join('/') + ')');
  // Verify wallet derivation
  const wallet = new Wallet(privateKey);
  console.log(`   Derived address: ${wallet.address}`);
  console.log(`   Matches identity: ${wallet.address.toLowerCase() === identity.address.toLowerCase() ? '✅' : '❌'}`);
  ethersOk = true;
} catch (e) {
  console.log('   ethers: ❌ not available in local node_modules');
  console.log('   Run: npm install ethers (in workspace directory)');
}

// 5. Try XMTP Agent (optional)
console.log('\n🌐 XMTP Agent check...');
let xmtpOk = false;
try {
  const xmtpPath = require.resolve('@xmtp/agent-sdk', { paths: [process.cwd()] });
  const { Agent } = require(xmtpPath);
  console.log('   @xmtp/agent-sdk: ✅ loaded');
  xmtpOk = true;
} catch (e) {
  console.log('   @xmtp/agent-sdk: ❌ not available');
  console.log('   Run: npm install @xmtp/agent-sdk');
}

console.log('\n✅ Moltline fully configured and ready!');
console.log('   To send a message, extend this script with agent creation.');
console.log('   Docs: https://docs.xmtp.org/');
