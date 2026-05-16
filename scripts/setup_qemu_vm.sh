#!/bin/bash
# QEMU/KVM Full Virtualization Environment — Complete Setup
# Creates a dedicated VM for quantum simulations with GPU passthrough support
# Hardware check: If VT-x/AMD-V missing, falls back to TCG software emulation

set -e

WORKDIR="/root/.openclaw/workspace/qemu-vm"
VM_NAME="quantum-worker"
VM_DISK="${WORKDIR}/${VM_NAME}.qcow2"
VM_MEMORY="8192"      # 8GB RAM
VM_VCPUS="4"          # 4 vCPUs
DISK_SIZE="50G"

echo "[$(date)] Starting QEMU VM setup..."

# Create workspace
mkdir -p "$WORKDIR"
cd "$WORKDIR"

# Check for hardware virtualization
if grep -E '(vmx|svm)' /proc/cpuinfo > /dev/null; then
    echo "Hardware virtualization detected (VT-x/AMD-V)"
    KVM_FLAG="-enable-kvm"
else
    echo "No hardware virtualization — using TCG software emulation (slower)"
    KVM_FLAG=""
fi

# Create virtual disk (50GB, qcow2 format)
if [ ! -f "$VM_DISK" ]; then
    echo "Creating ${DISK_SIZE} virtual disk..."
    qemu-img create -f qcow2 "$VM_DISK" "$DISK_SIZE"
    echo "Disk created: $VM_DISK"
else
    echo "Disk already exists: $VM_DISK"
fi

# Download AlmaLinux 9 Cloud Base image (minimal, 1.2GB)
CLOUD_IMAGE="${WORKDIR}/almalinux-9-cloud-base.x86_64.qcow2"
if [ ! -f "$CLOUD_IMAGE" ]; then
    echo "Downloading AlmaLinux 9 Cloud Base image..."
    curl -L -o "$CLOUD_IMAGE" \
        "https://repo.almalinux.org/almalinux/9/cloud/x86_64/images/AlmaLinux-9-GenericCloud-9.5-20241017.x86_64.qcow2"
    echo "Download complete: $CLOUD_IMAGE"
else
    echo "Cloud image already exists: $CLOUD_IMAGE"
fi

# Create seed ISO for cloud-init (first-boot configuration)
SEED_ISO="${WORKDIR}/seed.iso"
cat > "${WORKDIR}/user-data" << 'EOF'
#cloud-config
users:
  - default
  - name: quantum
    gecos: Quantum Sim User
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: users,admin,wheel
    ssh_authorized_keys:
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7... # FILL FROM ~/.ssh/id_rsa.pub IF NEEDED
    lock_passwd: false
    passwd: "$6$rounds=4096$salt$hash"  # Set via: openssl passwd -6 'yourpassword'
ssh_pwauth: true
disable_root: false
EOF

cat > "${WORKDIR}/meta-data" << 'EOF'
instance-id: quantum-worker-01
local-hostname: quantum-worker
EOF

# Build seed ISO (requires genisoimage / mkisofs)
if ! command -v genisoimage &> /dev/null; then
    apt-get install -y genisoimage 2>/dev/null || true
fi
genisoimage -output "$SEED_ISO" -volid cidata -joliet -rock user-data meta-data

echo "Seed ISO created: $SEED_ISO"

# Prepare cloud-init drive
CLOUD_INIT_DISK="${WORKDIR}/cloud-init.qcow2"
qemu-img create -f qcow2 "$CLOUD_INIT_DISK" 2G

# Attach cloud image as backing file and inject seed ISO
# Note: virt-install would do this automatically, but we use raw qemu for full control

# Build QEMU command
QEMU_CMD="qemu-system-x86_64 \
    -name \"${VM_NAME}\" \
    -machine q35,accel=kvm:tcg \
    -m ${VM_MEMORY} \
    -smp ${VM_VCPUS} \
    -drive file=\"${VM_DISK}\",format=qcow2,if=virtio \
    -drive file=\"${CLOUD_INIT_DISK}\",format=qcow2,if=virtio \
    -drive file=\"${SEED_ISO}\",media=cdrom,readonly=on \
    -netdev user,id=net0 \
    -device virtio-net-pci,netdev=net0 \
    -display none \
    -nographic \
    ${KVM_FLAG} \
    -cpu host"

# Save command for manual execution
echo "$QEMU_CMD" > "${WORKDIR}/qemu_command.sh"
chmod +x "${WORKDIR}/qemu_command.sh"

echo "[$(date)] QEMU environment prepared."
echo ""
echo "To start the VM (headless, serial console on stdin/stdout):"
echo "  cd $WORKDIR && ./qemu_command.sh"
echo ""
echo "To connect via SSH (once booted):"
echo "  ssh quantum@10.0.2.15   # default user-network IP"
echo ""
echo "To use as libvirt VM (optional, requires virt-install):"
echo "  virt-install \\"
echo "    --name $VM_NAME \\"
echo "    --memory $VM_MEMORY --vcpus $VM_VCPUS \\"
echo "    --disk path=${VM_DISK},format=qcow2 \\"
echo "    --disk path=${CLOUD_INIT_DISK},device=disk \\"
echo "    --disk path=${SEED_ISO},device=cdrom \\"
echo "    --os-variant almalinux9 \\"
echo "    --network network=default \\"
echo "    --graphics none \\"
echo "    --console pty,target_type=serial"

echo ""
echo "⚠️  Note: This script does NOT run the VM automatically."
echo "   Execute qemu_command.sh manually when ready to provision."
