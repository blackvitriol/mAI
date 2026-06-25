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

MODEL_ID="${LM_STUDIO_MODEL_ID:-}"
GPU_MODE="${LM_STUDIO_GPU:-max}"
CONTEXT_LENGTH="${LM_STUDIO_CONTEXT_LENGTH:-65536}"
if [ -n "${MODEL_ID}" ]; then
  echo "[lmstudio] Waiting for API before loading ${MODEL_ID}..."
  for i in $(seq 1 60); do
    if wget -qO- "http://127.0.0.1:${PORT}/v1/models" >/dev/null 2>&1; then
      break
    fi
    sleep 2
  done
  echo "[lmstudio] Loading model ${MODEL_ID} (gpu=${GPU_MODE}, context=${CONTEXT_LENGTH})..."
  if lms load "${MODEL_ID}" --gpu "${GPU_MODE}" --context-length "${CONTEXT_LENGTH}" -y; then
    echo "[lmstudio] Model ${MODEL_ID} loaded."
  else
    echo "[lmstudio] Warning: could not load ${MODEL_ID}. Check lms ls inside the container."
  fi
fi

PID_FILE="${LM_STUDIO_HOME}/.internal/llmster-pid.lock"
if [ -f "${PID_FILE}" ]; then
  echo "[lmstudio] Server ready (llmster pid $(cat "${PID_FILE}"))."
  exec tail --pid="$(cat "${PID_FILE}")" -f /dev/null
fi

echo "[lmstudio] Warning: pid file missing; keeping container alive."
exec tail -f /dev/null
