#!/usr/bin/env bash
# Copy unicli-hub framework files into a consuming repository.
# Does not clobber overlay (project-context, memory, mcp-servers, existing skills).
#
# Usage:
#   ./scripts/install-framework.sh --target /path/to/consumer [--dry-run]
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET=""
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$TARGET" || ! -d "$TARGET" ]]; then
  echo "usage: $0 --target /path/to/consumer [--dry-run]" >&2
  exit 2
fi
TARGET="$(cd "$TARGET" && pwd)"
if [[ "$TARGET" == "$SRC" ]]; then
  echo "refusing to install into unicli-hub itself" >&2
  exit 2
fi

SHA="$(git -C "$SRC" rev-parse HEAD)"
log() { printf '%s\n' "$*"; }
copy_file() {
  local rel="$1"
  local dest="$TARGET/$rel"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "COPY $rel"
    return
  fi
  mkdir -p "$(dirname "$dest")"
  cp "$SRC/$rel" "$dest"
  log "copied $rel"
}
copy_tree() {
  local rel="$1"
  if [[ ! -d "$SRC/$rel" ]]; then
    return
  fi
  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "COPYTREE $rel"
    return
  fi
  mkdir -p "$TARGET/$rel"
  # trailing slash: copy contents
  cp -R "$SRC/$rel/." "$TARGET/$rel/"
  log "copied $rel/"
}

log "--- unicli-hub install-framework ($SHA) -> $TARGET ---"

copy_tree ".unicli-hub/scripts"
# Templates: copy missing names only. Consumer-localized AGENTS.md.tmpl stays.
if [[ -d "$SRC/.unicli-hub/templates" ]]; then
  mkdir -p "$TARGET/.unicli-hub/templates"
  for f in "$SRC/.unicli-hub/templates"/*; do
    [[ -f "$f" ]] || continue
    bn="$(basename "$f")"
    if [[ -f "$TARGET/.unicli-hub/templates/$bn" ]]; then
      log "keep consumer template $bn"
    else
      copy_file ".unicli-hub/templates/$bn"
    fi
  done
fi

copy_file "sync.sh"
chmod +x "$TARGET/sync.sh" 2>/dev/null || true
copy_tree "hub/common"
copy_tree "hub/templates"
[[ -f "$SRC/hub/claude-hooks.json" ]] && copy_file "hub/claude-hooks.json"
[[ -f "$SRC/hub/cursor-hooks.json" ]] && copy_file "hub/cursor-hooks.json"
[[ -f "$SRC/hub/README.md" ]] && copy_file "hub/README.md"

# Hooks: copy missing; existing files are overlay (path guards, superproject commands).
mkdir -p "$TARGET/hub/hooks"
for f in "$SRC/hub/hooks"/*; do
  [[ -f "$f" ]] || continue
  bn="$(basename "$f")"
  if [[ -f "$TARGET/hub/hooks/$bn" ]]; then
    log "keep consumer hook $bn"
  else
    copy_file "hub/hooks/$bn"
  fi
done

mkdir -p "$TARGET/scripts/mcp"
for f in run-with-env.sh project-env.sh; do
  if [[ -f "$SRC/scripts/mcp/$f" ]]; then
    if [[ -f "$TARGET/scripts/mcp/$f" ]]; then
      if [[ "$DRY_RUN" -eq 1 ]]; then
        log "REPLACE scripts/mcp/$f"
      else
        cp "$SRC/scripts/mcp/$f" "$TARGET/scripts/mcp/$f"
        log "copied scripts/mcp/$f"
      fi
    else
      copy_file "scripts/mcp/$f"
    fi
  fi
done

# Additive skills / agents
if [[ -d "$SRC/hub/skills" ]]; then
  mkdir -p "$TARGET/hub/skills"
  for d in "$SRC/hub/skills"/*; do
    [[ -d "$d" ]] || continue
    name="$(basename "$d")"
    if [[ -e "$TARGET/hub/skills/$name" ]]; then
      log "keep consumer skill $name"
    else
      if [[ "$DRY_RUN" -eq 1 ]]; then
        log "ADD skill $name"
      else
        cp -R "$d" "$TARGET/hub/skills/$name"
        log "added skill $name"
      fi
    fi
  done
fi
if [[ -d "$SRC/hub/agents" ]]; then
  mkdir -p "$TARGET/hub/agents"
  for f in "$SRC/hub/agents"/*; do
    [[ -f "$f" ]] || continue
    bn="$(basename "$f")"
    if [[ -f "$TARGET/hub/agents/$bn" ]]; then
      log "keep consumer agent $bn"
    else
      copy_file "hub/agents/$bn"
    fi
  done
fi

mkdir -p "$TARGET/hub/registry"
for f in fanout.json hook-events.json agent-profiles.json; do
  if [[ -f "$SRC/hub/registry/$f" ]]; then
    if [[ -f "$TARGET/hub/registry/$f" ]]; then
      log "REVIEW merge hub/registry/$f (not overwritten)"
    else
      copy_file "hub/registry/$f"
    fi
  fi
done

if [[ "$DRY_RUN" -eq 0 ]]; then
  mkdir -p "$TARGET/.unicli-hub"
  cat > "$TARGET/.unicli-hub/VERSION" <<EOF
upstream=https://github.com/teelukira/unicli-hub
commit=$SHA
date=$(date +%F)
EOF
  log "wrote .unicli-hub/VERSION"
fi

log "--- next: cd $TARGET && ./sync.sh --fix && ./sync.sh --check ---"
log "overlay left intact: hub/project-context.md hub/memory hub/mcp-servers.json hub/kiro-steering existing skills/hooks/templates"
