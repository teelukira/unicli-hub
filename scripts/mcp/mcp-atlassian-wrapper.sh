#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# shellcheck source=project-env.sh
source "${SCRIPT_DIR}/project-env.sh"
load_project_env "${REPO_ROOT}"

export FASTMCP_LOG_LEVEL="${FASTMCP_LOG_LEVEL:-ERROR}"
export FASTMCP_SHOW_CLI_BANNER="${FASTMCP_SHOW_CLI_BANNER:-false}"
export FASTMCP_CHECK_FOR_UPDATES="${FASTMCP_CHECK_FOR_UPDATES:-off}"
export TOOLSETS="${TOOLSETS:-all}"

if [[ -z "${JIRA_URL:-}" ]]; then
  echo "mcp-atlassian-wrapper: JIRA_URL is required in environment, .env, or .env.local" >&2
  exit 2
fi

if [[ -z "${JIRA_PERSONAL_TOKEN:-}" && ( -z "${JIRA_USERNAME:-}" || -z "${JIRA_API_TOKEN:-}" ) && ( -z "${JIRA_USERNAME:-}" || -z "${JIRA_TOKEN:-}" ) ]]; then
  echo "mcp-atlassian-wrapper: set JIRA_PERSONAL_TOKEN, or JIRA_USERNAME plus JIRA_API_TOKEN/JIRA_TOKEN" >&2
  exit 2
fi

exec uvx mcp-atlassian "$@"
