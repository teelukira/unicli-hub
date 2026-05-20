#!/usr/bin/env bash
set -euo pipefail
# Consume hook payload (JSON on stdin)
cat >/dev/null
# Allow all tool/shell actions; replace with ./.unicli-rules/sync.sh --fix outputs when available.
echo "{\"permission\":\"allow\"}"
