#!/usr/bin/env node
/**
 * QEMU VM Orchestrator — UEFI boot, AlmaLinux cloud, TCG or KVM
 * CPU: uses 'max' for TCG (meets x86-64-v2), 'host' for KVM
 * Port forward: host 2222 -> guest 22 (SSH)
 */

const fs = require('fs');
const path = require('path');
const { spawn, execSync } = require('child_process');

const WORKDIR = path.resolve(process.cwd(), 'qemu-vm');
const VM_NAME = 'quantum-worker';
const VM_DISK = path.join(WORKDIR, `${VM_NAME}.qcow2`);
const CLOUD_IMAGE_URL = 'https://repo.almalinux.org/almalinux/9/cloud/x86_64/images/AlmaLinux-9-GenericCloud-latest.x86_64.qcow2';
const CLOUD_IMAGE_NAME = 'AlmaLinux-9-GenericCloud-latest.x86_64.qcow2';
const CLOUD_IMAGE_PATH = path.join(WORKDIR, CLOUD_IMAGE_NAME);
const DISK_SIZE = '50G';
const VM_MEMORY = '1024';
const VM_VCPUS = '2';
const OVMF_CODE = '/usr/share/OVMF/OVMF_CODE_4M.fd';
const OVMF_VARS = '/usr/share/OVMF/OVMF_VARS_4M.fd';

function log(msg) {
    const ts = new Date().toISOString();
    console.log(`[${ts}] ${msg}`);
}

function checkPrereqs() {
    log('Checking prerequisites...');
    ['/usr/bin/qemu-img','/usr/bin/qemu-system-x86_64'].forEach(p => {
        try { fs.accessSync(p, fs.constants.X_OK); } catch (e) { log(`ERROR: missing ${p}`); process.exit(1); }
    });
    if (!fs.existsSync('/usr/bin/genisoimage') && !fs.existsSync('/usr/bin/mkisofs')) {
        log('Installing genisoimage...');
        try { execSync('apt-get update',{stdio:'pipe'}); execSync('apt-get install -y genisoimage',{stdio:'pipe'}); }
        catch(e){ log('ERROR: install genisoimage failed'); process.exit(1); }
    }
    log('Prerequisites OK.');
}

function setup() {
    log('Starting VM setup...');
    checkPrereqs();
    fs.mkdirSync(WORKDIR,{recursive:true});
    process.chdir(WORKDIR);
    log(`Workspace: ${WORKDIR}`);

    if (!fs.existsSync(CLOUD_IMAGE_PATH)) {
        log('Downloading AlmaLinux cloud image...');
        const curl = spawn('curl',['-L','-o',CLOUD_IMAGE_PATH,CLOUD_IMAGE_URL]);
        curl.stderr.on('data',d=>process.stderr.write(d));
        curl.on('close',code=>{
            if(code!==0) return fail('curl');
            log('Cloud image downloaded.');
            afterCloudImage();
        });
    } else {
        log('Cloud image already present.');
        afterCloudImage();
    }

    function afterCloudImage() {
        if (!fs.existsSync(VM_DISK)) {
            log('Copying cloud image to VM disk...');
            try { fs.copyFileSync(CLOUD_IMAGE_PATH, VM_DISK); log('VM disk ready.'); }
            catch(e){ return fail('copy VM disk'); }
        } else { log('VM disk exists — skipping copy.'); }
        afterDisk();
    }

    function afterDisk() {
        log('Creating cloud-init seed ISO...');
        const sshPub = path.join(process.env.HOME||'/root','.ssh','id_rsa.pub');
        let key=''; if(fs.existsSync(sshPub)) key=fs.readFileSync(sshPub,'utf8').trim();
        const userData = `#cloud-config
users:
  - default
  - name: quantum
    gecos: Quantum Sim User
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: users,admin,wheel
    lock_passwd: false
    ssh_authorized_keys:
      - ${key || 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7... placeholder'}
ssh_pwauth: true
disable_root: false
chpasswd:
  expire: false
  list: |
    quantum:QuantumPass123!
`;
        const metaData = `instance-id: quantum-worker-01\nlocal-hostname: quantum-worker\n`;
        fs.writeFileSync(path.join(WORKDIR,'user-data'),userData);
        fs.writeFileSync(path.join(WORKDIR,'meta-data'),metaData);
        const seedIso = path.join(WORKDIR,'seed.iso');
        const geniso = spawn('genisoimage',['-output',seedIso,'-volid','cidata','-joliet','-rock','user-data','meta-data']);
        geniso.on('close',code=>{ if(code!==0) return fail('genisoimage'); log('Seed ISO created.'); afterSeed(); });
    }

    function afterSeed() {
        const cidisk = path.join(WORKDIR,'cloud-init.qcow2');
        if (!fs.existsSync(cidisk)) {
            log('Creating cloud-init disk...');
            const qi = spawn('qemu-img',['create','-f','qcow2',cidisk,'2G']);
            qi.on('close',code=>{ if(code!==0) return fail('cloud-init disk'); log('Cloud-init disk created.'); afterCloudInit(); });
        } else { log('Cloud-init disk exists — skipping.'); afterCloudInit(); }
    }

    function afterCloudInit() {
        const ovmfVars = path.join(WORKDIR,'OVMF_VARS.fd');
        if (!fs.existsSync(ovmfVars) && fs.existsSync(OVMF_VARS)) {
            fs.copyFileSync(OVMF_VARS, ovmfVars);
            log('OVMF_VARS.fd copied.');
        }
        buildCmd();
    }

    function buildCmd() {
        log('Building QEMU command...');
        let kvmFlag=''; let cpuModel='max';
        try {
            const cpuinfo = fs.readFileSync('/proc/cpuinfo','utf8');
            if (cpuinfo.includes('vmx') || cpuinfo.includes('svm')) { kvmFlag='-enable-kvm'; cpuModel='host'; log('KVM → host CPU.'); }
            else log('TCG mode → max CPU.');
        } catch(e){ log('CPU check failed → using max.'); }

        const cmd = `qemu-system-x86_64 \\
    -name "${VM_NAME}" \\
    -machine q35,accel=kvm:tcg \\
    -m ${VM_MEMORY} \\
    -smp ${VM_VCPUS} \\
    -drive file="${VM_DISK}",format=qcow2,if=virtio \\
    -drive file="${path.join(WORKDIR,'cloud-init.qcow2')}",format=qcow2,if=virtio \\
    -drive file="${path.join(WORKDIR,'seed.iso')}",media=cdrom,readonly=on \\
    -drive if=pflash,format=raw,readonly=on,file=${OVMF_CODE} \\
    -drive if=pflash,format=raw,file=${path.join(WORKDIR,'OVMF_VARS.fd')} \\
    -netdev user,id=net0,hostfwd=tcp::2222-:22 \\
    -device virtio-net-pci,netdev=net0 \\
    -display none \\
    -nographic \\
    ${kvmFlag} \\
    -cpu ${cpuModel}`;

        fs.writeFileSync(path.join(WORKDIR,'qemu_command.sh'), cmd+'\n');
        fs.chmodSync(path.join(WORKDIR,'qemu_command.sh'),0o755);
        log('QEMU command written.');
        log('Setup complete. Use: node qemu_setup_orchestrator.js start');
    }

    function fail(stage) { log(`ERROR in ${stage}`); process.exit(1); }
}

function start() {
    log('Starting QEMU VM...');
    const cmdPath = path.join(WORKDIR,'qemu_command.sh');
    if (!fs.existsSync(cmdPath)) { log('ERROR: Run setup first.'); process.exit(1); }
    try { fs.unlinkSync(path.join(WORKDIR,'qemu.pid')); } catch(e){}
    const qemu = spawn('/bin/bash',[cmdPath],{
        cwd: WORKDIR,
        stdio:['ignore','inherit','inherit'],
        detached: true
    });
    fs.writeFileSync(path.join(WORKDIR,'qemu.pid'), qemu.pid.toString());
    log(`QEMU PID ${qemu.pid}.`);
    process.exit(0);
}

function stop() {
    log('Stopping QEMU VM...');
    const pidFile = path.join(WORKDIR,'qemu.pid');
    if (!fs.existsSync(pidFile)) { log('No PID file; trying pkill...'); try { execSync('pkill -f "qemu-system-x86_64.*quantum-worker"'); } catch(e){} process.exit(0); }
    const pid = parseInt(fs.readFileSync(pidFile,'utf8').trim(),10);
    try { process.kill(pid,'SIGTERM'); } catch(e){}
    setTimeout(()=>{ try{process.kill(pid,'SIGKILL')}catch(e){} },5000);
    process.exit(0);
}

function status() {
    const pidFile = path.join(WORKDIR,'qemu.pid');
    if(!fs.existsSync(pidFile)){ log('VM STOPPED (no pid)'); process.exit(0); }
    const pid = parseInt(fs.readFileSync(pidFile,'utf8').trim(),10);
    try{ process.kill(pid,0); log(`VM RUNNING (PID ${pid})`); process.exit(0); }
    catch(e){ log('Stale PID — VM not running'); fs.unlinkSync(pidFile); process.exit(1); }
}

const action = process.argv[2];
switch(action){
    case 'setup':   setup(); break;
    case 'start':   start(); break;
    case 'stop':    stop(); break;
    case 'status':  status(); break;
    case 'full':    setup(); start(); break;
    default:
        console.log(`
QEMU VM Orchestrator — Usage:

  node qemu_setup_orchestrator.js setup     Prepare disk (download, cloud-init, UEFI)
  node qemu_setup_orchestrator.js start    Launch VM (detached)
  node qemu_setup_orchestrator.js stop     Shutdown VM
  node qemu_setup_orchestrator.js status   Show state
  node qemu_setup_orchestrator.js full     Setup then start

Spec: ${VM_MEMORY} MB RAM, ${VM_VCPUS} vCPUs, ${DISK_SIZE} disk.
UEFI via OVMF. TCG fallback with 'max' CPU.
SSH: host localhost:2222 → guest quantum@localhost:22
`);
        process.exit(1);
}
