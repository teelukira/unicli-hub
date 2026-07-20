#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# shellcheck source=project-env.sh
source "${SCRIPT_DIR}/project-env.sh"
load_project_env "${REPO_ROOT}"

if [[ "$#" -eq 0 ]]; then
  echo "run-with-env: command is required" >&2
  exit 2
fi

command="$1"
shift
if [[ "${command}" == */* && "${command}" != /* ]]; then
  command="${REPO_ROOT}/${command#./}"
fi

exec "${command}" "$@"
