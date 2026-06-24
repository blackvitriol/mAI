#!/bin/sh
set -e

for dir in \
  /home/node/.openclaw/state \
  /home/node/.openclaw/agents/main/agent/plugins
do
  if [ -d "$dir" ]; then
    chown -R node:node "$dir" 2>/dev/null || true
  fi
done

exec runuser -u node -- "$@"
