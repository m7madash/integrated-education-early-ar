/**
 * QEMU VM Manager — Stop VM (Node.js wrapper)
 * Sends ACPI shutdown or kills QEMU process
 * Single-binary invocation: node stop_vm.js
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const WORKDIR = path.resolve(process.cwd(), 'qemu-vm');
const PID_FILE = path.join(WORKDIR, 'qemu.pid');

console.log(`[${new Date().toISOString()}] Stopping QEMU VM...`);

// If PID file exists, try graceful shutdown
if (fs.existsSync(PID_FILE)) {
    const pid = parseInt(fs.readFileSync(PID_FILE, 'utf8').trim(), 10);
    console.log(`Found PID ${pid} — attempting graceful ACPI shutdown...`);

    // Send ACPI power button event via QEMU monitor (if accessible)
    // For now, we use kill -SIGTERM which triggers guest ACPI if configured
    process.kill(pid, 'SIGTERM');

    // Wait up to 30s for graceful exit
    const timeout = setTimeout(() => {
        console.log('Graceful shutdown timed out — forcing kill...');
        try { process.kill(pid, 'SIGKILL'); } catch (e) {}
    }, 30000);

    // Poll for PID disappearance
    const interval = setInterval(() => {
        try {
            process.kill(pid, 0); // throws if dead
        } catch (e) {
            clearInterval(interval);
            clearTimeout(timeout);
            console.log('VM stopped.');
            fs.unlinkSync(PID_FILE);
            process.exit(0);
        }
    }, 1000);

} else {
    // Fallback: find QEMU process by name pattern
    console.log('No PID file found — searching for QEMU process...');
    exec("pgrep -f 'qemu-system-x86_64.*quantum-worker'", (err, stdout, stderr) => {
        if (err || !stdout.trim()) {
            console.log('No running QEMU VM found.');
            process.exit(0);
        }
        const pid = parseInt(stdout.trim(), 10);
        console.log(`Found QEMU PID ${pid} — terminating...`);
        process.kill(pid, 'SIGTERM');
        setTimeout(() => {
            try { process.kill(pid, 'SIGKILL'); } catch (e) {}
        }, 5000);
        process.exit(0);
    });
}
