#!/bin/bash
set -euo pipefail

export PUPPETEER_CACHE_DIR="${PUPPETEER_CACHE_DIR:-/home/node/.n8n/puppeteer-cache}"
mkdir -p "${PUPPETEER_CACHE_DIR}"

MARKER="/home/node/.n8n/.deps-setup-complete"
PKG="/home/node/.n8n/nodes/package.json"

if [ -f "${MARKER}" ] && [ "${A7_SETUP_FORCE:-0}" != "1" ]; then
  echo "[n8n] Dependencies already set up (init). Run init.cmd --force to redo."
  exit 0
fi

puppeteer_pkg() {
  local base="/home/node/.n8n/nodes/node_modules/n8n-nodes-puppeteer/node_modules/puppeteer"
  if [ -f "${base}/package.json" ]; then
    echo "${base}"
    return 0
  fi
  return 1
}

chrome_ready() {
  compgen -G "${PUPPETEER_CACHE_DIR}/chrome/*/chrome-linux64/chrome" >/dev/null 2>&1
}

if pkg="$(puppeteer_pkg)"; then
  if chrome_ready; then
    echo "[n8n] Puppeteer Chrome already cached."
  else
    echo "[n8n] Downloading Puppeteer Chrome (one-time)..."
    (
      cd "${pkg}"
      npx --yes puppeteer browsers install chrome
    )
    echo "[n8n] Puppeteer Chrome ready."
  fi
else
  echo "[n8n] Skipping Puppeteer Chrome (install n8n-nodes-puppeteer first)."
fi

if [ -f "${PKG}" ]; then
  echo "[n8n] Installing community nodes..."
  (
    cd /home/node/.n8n/nodes
    npm install --omit=dev --no-audit --no-fund
  )
else
  echo "[n8n] No community nodes yet (add via n8n UI later)."
fi

touch "${MARKER}"
echo "[n8n] Dependency setup complete."
