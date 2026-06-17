#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

load_env_file() {
  local file="$1"
  [[ -f "${file}" ]] || return 0
  set -a
  # shellcheck disable=SC1090
  source "${file}"
  set +a
}

load_env_file "${REPO_ROOT}/.env"
load_env_file "${REPO_ROOT}/.env.local"

args=()
if [[ -n "${CONTEXT7_API_KEY:-}" ]]; then
  args+=(--api-key "${CONTEXT7_API_KEY}")
fi

exec npx -y @upstash/context7-mcp@latest "${args[@]}" "$@"
