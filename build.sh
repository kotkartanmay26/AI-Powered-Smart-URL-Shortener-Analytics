
#!/usr/bin/env bash
set -euo pipefail

# Make Cargo/Rust point to writable directories (fixes "Read-only file system (os error 30)")
export CARGO_HOME="$HOME/.cargo"
export RUSTUP_HOME="$HOME/.rustup"
export PIP_CACHE_DIR="$HOME/.pip-cache"

mkdir -p "$CARGO_HOME" "$RUSTUP_HOME" "$PIP_CACHE_DIR"

echo "=== Python version ==="
python --version

echo "=== Node.js version ==="
node --version
npm --version

echo "=== Building frontend ==="
cd frontend
if [ -f package-lock.json ]; then
  npm ci --no-audit --no-fund
else
  npm install --no-audit --no-fund
fi
npm run build
cd ..

echo "=== Upgrading pip, setuptools, wheel ==="
cd backend
python -m pip install --upgrade pip setuptools wheel

echo "=== Installing backend requirements (prefer binary wheels) ==="
python -m pip install \
  --prefer-binary \
  --no-cache-dir \
  -r requirements.txt
cd ..

echo "=== Build complete ==="
