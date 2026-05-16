#!/bin/bash
# Quantum Environment Initializer — runs inside the VM once
# Installs: Python 3.13 (if not present), Qiskit, Cirq, Pennylane, Strawberry Fields, SymPy, SciPy, NumPy, Jupyter, ngrok tunnel
# Designed for AlmaLinux 9 / RHEL 9 compatible systems

set -e

echo "========================================"
echo " Quantum Environment Initializer — $(date)"
echo "========================================"

# Update system
echo "[1/7] Updating system packages..."
dnf update -y || yum update -y

# Install EPEL and development tools
echo "[2/7] Installing development tools and Python 3.13..."
if command -v dnf &> /dev/null; then
    dnf install -y epel-release || true
    dnf install -y python3.13 python3.13-devel gcc gcc-c++ make \
        redhat-rpm-config \
        openssl-devel bzip2-devel libffi-devel \
        zlib-devel wget curl git \
        which || true
elif command -v yum &> /dev/null; then
    yum install -y epel-release || true
    yum install -y python3.13 python3.13-devel gcc gcc-c++ make \
        redhat-rpm-config \
        openssl-devel bzip2-devel libffi-devel \
        zlib-devel wget curl git \
        which || true
fi

# Ensure python3.13 is default
if ! command -v python3.13 &> /dev/null; then
    echo "ERROR: Python 3.13 installation failed. Aborting."
    exit 1
fi

# Create alternatives if python3 points elsewhere
if command -v python3 &> /dev/null && [[ "$(python3 --version 2>&1)" != *"3.13"* ]]; then
    if command -v update-alternatives &> /dev/null; then
        update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1 || true
        update-alternatives --set python3 /usr/bin/python3.13 || true
    else
        ln -sf /usr/bin/python3.13 /usr/bin/python3 || true
    fi
fi

# Upgrade pip
echo "[3/7] Installing pip for Python 3.13..."
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.13 || {
    python3.13 -m ensurepip --upgrade || true
}
python3.13 -m pip install --upgrade pip setuptools wheel

# Create dedicated user (if not already)
if ! id -u quantum &> /dev/null; then
    echo "[4/7] Creating 'quantum' user..."
    useradd -m -s /bin/bash quantum || true
    echo "quantum:QuantumPass123!" | chpasswd || true
    usermod -aG wheel quantum || true
fi

# Install quantum Python packages in user site + system-wide
echo "[5/7] Installing quantum computing libraries..."
PYTHON_CMD="python3.13 -m pip"

# System-wide install
$PYTHON_CMD install --no-cache-dir --upgrade \
    qiskit>=1.3 \
    qiskit-aer>=0.15 \
    qiskit-ibmq-provider>=0.20 \
    cirq>=1.4 \
    pennylane>=0.41 \
    strawberryfields>=0.24 \
    sympy>=1.13 \
    scipy>=1.14 \
    numpy>=2.1 \
    matplotlib>=3.9 \
    jupyterlab>=4.3 \
    ipykernel>=6.29 \
    plotly>=5.24 \
    pillow>=10.4 \
    requests>=2.32 \
    tqdm>=4.67 \
    ngrok-api>=1.0 || true

# Also install to quantum user's site-packages if user exists
if id -u quantum &> /dev/null; then
    sudo -u quantum $PYTHON_CMD install --user --no-cache-dir --upgrade \
        qiskit cirq pennylane strawberryfields sympy scipy numpy matplotlib || true
fi

# Register Jupyter kernel for Python 3.13
echo "[6/7] Setting up Jupyter kernel..."
python3.13 -m ipykernel install --user --name python3.13 --display-name "Python 3.13 (Quantum)" || true

# Install and configure ngrok (for tunneling)
if command -v ngrok &> /dev/null; then
    echo "ngrok already installed."
else
    echo "[7/7] Installing ngrok tunnel..."
    curl -o /tmp/ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip || true
    unzip -o /tmp/ngrok.zip -d /usr/local/bin/ || true
    chmod +x /usr/local/bin/ngrok || true
    rm -f /tmp/ngrok.zip
fi

# Create quantum workspace in user home
mkdir -p /home/quantum/{projects,data,notebooks} || true
chown -R quantum:quantum /home/quantum || true

echo ""
echo "========================================"
echo " Quantum environment setup COMPLETE"
echo "========================================"
echo ""
echo "Installed packages:"
echo "  - Python $(python3.13 --version 2>&1)"
echo "  - Qiskit $(python3.13 -c 'import qiskit; print(qiskit.__version__)' 2>/dev/null || echo '?')"
echo "  - Cirq $(python3.13 -c 'import cirq; print(cirq.__version__)' 2>/dev/null || echo '?')"
echo "  - PennyLane $(python3.13 -c 'import pennylane; print(pennylane.__version__)' 2>/dev/null || echo '?')"
echo "  - Strawberry Fields $(python3.13 -c 'import strawberryfields; print(strawberryfields.__version__)' 2>/dev/null || echo '?')"
echo ""
echo "Next steps:"
echo "1. Start the VM: node /root/.openclaw/workspace/scripts/start_vm.js"
echo "2. SSH into VM (user=quantum, pass=QuantumPass123!, IP typically 10.0.2.15)"
echo "3. Run: jupyter lab --ip=0.0.0.0 --port=8888 --no-browser"
echo "4. Tunnel: ngrok http 8888"
echo ""
echo "بفضل الله، البيئة جاهزة للعمليات الكمية."
