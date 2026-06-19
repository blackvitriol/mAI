#!/bin/bash
set -euo pipefail

export LM_STUDIO_HOME="${LM_STUDIO_HOME:-/root/.lmstudio}"
export PATH="${LM_STUDIO_HOME}/bin:${PATH}"
export LMS_SERVER_HOST="${LMS_SERVER_HOST:-0.0.0.0}"

wait_for_lms() {
  local i
  for i in $(seq 1 90); do
    if [ -x "${LM_STUDIO_HOME}/bin/lms" ] && "${LM_STUDIO_HOME}/bin/lms" --help >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  echo "[lmstudio] lms binary not ready after install"
  return 1
}

if [ ! -x "${LM_STUDIO_HOME}/bin/lms" ]; then
  echo "[lmstudio] Installing llmster (GPU bundle selected when NVIDIA is visible)..."
  curl -fsSL https://lmstudio.ai/install.sh | bash
  wait_for_lms
fi

rm -f "${LM_STUDIO_HOME}/.internal/llmster-pid.lock" 2>/dev/null || true

echo "[lmstudio] Starting daemon..."
lms daemon up

PORT="${LM_STUDIO_PORT:-1234}"
echo "[lmstudio] Starting API server on ${LMS_SERVER_HOST}:${PORT}..."
lms server start --port "${PORT}" --bind "${LMS_SERVER_HOST}"

PID_FILE="${LM_STUDIO_HOME}/.internal/llmster-pid.lock"
if [ -f "${PID_FILE}" ]; then
  echo "[lmstudio] Server ready (llmster pid $(cat "${PID_FILE}"))."
  exec tail --pid="$(cat "${PID_FILE}")" -f /dev/null
fi

echo "[lmstudio] Warning: pid file missing; keeping container alive."
exec tail -f /dev/null
