#!/bin/bash
set -euo pipefail

export PUPPETEER_CACHE_DIR="${PUPPETEER_CACHE_DIR:-/home/node/.n8n/puppeteer-cache}"
mkdir -p "${PUPPETEER_CACHE_DIR}"

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

install_chrome() {
  local pkg
  if ! pkg="$(puppeteer_pkg)"; then
    echo "[n8n] n8n-nodes-puppeteer not installed yet; Chrome install runs on next boot after community node is present."
    return 0
  fi

  if chrome_ready; then
    echo "[n8n] Puppeteer Chrome already cached at ${PUPPETEER_CACHE_DIR}"
    return 0
  fi

  echo "[n8n] Downloading Puppeteer Chrome (one-time, cached in n8n data volume)..."
  (
    cd "${pkg}"
    npx --yes puppeteer browsers install chrome
  )
  echo "[n8n] Puppeteer Chrome ready."
}

install_chrome

if [ -f /home/node/.n8n/nodes/package.json ]; then
  echo "[n8n] Ensuring community nodes are installed..."
  (cd /home/node/.n8n/nodes && npm install --omit=dev --no-audit --no-fund) || true
fi

exec n8n "$@"
