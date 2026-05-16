/**
 * QEMU VM Manager — Start VM (Node.js wrapper)
 * Executes the prepared QEMU command with proper working directory
 * Single-binary invocation: node start_vm.js
 */

const { spawn } = require('child_process');
const path = require('path');

const WORKDIR = path.resolve(process.cwd(), 'qemu-vm');
const CMD_PATH = path.join(WORKDIR, 'qemu_command.sh');

console.log(`[${new Date().toISOString()}] Starting QEMU VM...`);
console.log(`Workdir: ${WORKDIR}`);
console.log(`Command script: ${CMD_PATH}`);

// Verify command script exists
const fs = require('fs');
if (!fs.existsSync(CMD_PATH)) {
    console.error(`ERROR: ${CMD_PATH} not found. Run setup_qemu_vm.sh first.`);
    process.exit(1);
}

// Execute qemu_command.sh as a child process
// QEMU will run in foreground until VM shuts down
const qemuProc = spawn('/bin/bash', [CMD_PATH], {
    cwd: WORKDIR,
    stdio: 'inherit',
    detached: false
});

qemuProc.on('exit', (code, signal) => {
    console.log(`[${new Date().toISOString()}] QEMU VM exited with code=${code} signal=${signal}`);
    process.exit(code || 0);
});

qemuProc.on('error', (err) => {
    console.error(`[${new Date().toISOString()}] Failed to start QEMU:`, err.message);
    process.exit(1);
});

// Handle SIGINT/SIGTERM gracefully
process.on('SIGINT', () => {
    console.log('\nReceived SIGINT — shutting down QEMU VM...');
    qemuProc.kill('SIGTERM');
});

process.on('SIGTERM', () => {
    console.log('\nReceived SIGTERM — shutting down QEMU VM...');
    qemuProc.kill('SIGTERM');
});
