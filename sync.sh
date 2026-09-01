#!/usr/bin/env bash
# Thin wrapper around sync.py for POSIX shells.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$ROOT/sync.py" "$@"
fi
if command -v python >/dev/null 2>&1; then
  exec python "$ROOT/sync.py" "$@"
fi
echo "python3 or python is required to run UniCLI-Hub sync" >&2
exit 1
