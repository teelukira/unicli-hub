#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# shellcheck source=project-env.sh
source "${SCRIPT_DIR}/project-env.sh"
load_project_env "${REPO_ROOT}"

export NODE_TLS_REJECT_UNAUTHORIZED="${NODE_TLS_REJECT_UNAUTHORIZED:-0}"

if [[ -z "${GITLAB_PERSONAL_ACCESS_TOKEN:-}" ]]; then
  echo "gitlab-wrapper: GITLAB_PERSONAL_ACCESS_TOKEN is required in environment, .env, or .env.local" >&2
  exit 2
fi

if [[ -z "${GITLAB_API_URL:-}" ]]; then
  echo "gitlab-wrapper: GITLAB_API_URL is required in environment, .env, or .env.local" >&2
  exit 2
fi

exec npx -y @modelcontextprotocol/server-gitlab "$@"
