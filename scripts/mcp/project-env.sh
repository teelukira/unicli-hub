#!/usr/bin/env bash

find_primary_worktree() {
  local repo_root="$1"
  local line
  while IFS= read -r line; do
    if [[ "${line}" == worktree\ * ]]; then
      printf '%s\n' "${line#worktree }"
      return 0
    fi
  done < <(git -C "${repo_root}" worktree list --porcelain 2>/dev/null)
  return 1
}

load_env_file() {
  local file="$1"
  [[ -f "${file}" ]] || return 0
  set -a
  # shellcheck disable=SC1090
  source "${file}"
  set +a
}

load_env_root() {
  local root="$1"
  load_env_file "${root}/.env"
  load_env_file "${root}/.env.local"
}

load_project_env() {
  local repo_root="$1"
  local primary_root
  local inherited_exports

  [[ "${UNICLI_HUB_ENV_LOADED:-}" == "1" ]] && return 0

  repo_root="$(cd "${repo_root}" && pwd -P)"
  inherited_exports="$(export -p | sed 's/^declare -x /export /')"
  primary_root="$(find_primary_worktree "${repo_root}" || true)"

  if [[ -n "${primary_root}" ]]; then
    primary_root="$(cd "${primary_root}" && pwd -P)"
    if [[ "${primary_root}" != "${repo_root}" ]]; then
      load_env_root "${primary_root}"
    fi
  fi
  load_env_root "${repo_root}"

  eval "${inherited_exports}"
  export UNICLI_HUB_ENV_LOADED=1
}
