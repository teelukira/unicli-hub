#!/usr/bin/env python3
"""auto_update.py — Fast, session-scoped auto-updater for UniCLI-Hub.

Ensures the repository is updated to the latest upstream commit and synced
exactly once per AI CLI session.
"""

from __future__ import annotations

import fcntl
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CACHE_DIR = ROOT / ".unicli-hub"
SESSION_CACHE_FILE = CACHE_DIR / ".session_cache.json"
LOCK_FILE = CACHE_DIR / ".sync.lock"

# Default session debounce fallback (if no explicit session_id is provided): 10 minutes
DEFAULT_DEBOUNCE_SECONDS = 600


def is_auto_update_disabled() -> bool:
    if os.environ.get("UNICLI_DISABLE_AUTO_UPDATE", "").lower() in ("1", "true", "yes"):
        return True
    if os.environ.get("UNICLI_AUTO_UPDATE", "").lower() in ("0", "false", "no"):
        return True
    return False


def load_session_cache() -> dict:
    if not SESSION_CACHE_FILE.exists():
        return {}
    try:
        data = json.loads(SESSION_CACHE_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def is_session_already_checked(session_id: str | None, debounce_sec: int = DEFAULT_DEBOUNCE_SECONDS) -> bool:
    cache = load_session_cache()
    now = time.time()

    # 1. If explicit session_id is provided, check if it was already processed
    if session_id:
        checked_sessions = cache.get("sessions", {})
        if session_id in checked_sessions:
            last_time = checked_sessions[session_id]
            # Keep valid for 24 hours per session_id
            if (now - last_time) < 86400:
                return True

    # 2. Fallback debounce based on last global check timestamp
    last_global_check = cache.get("last_check_time", 0)
    if (now - last_global_check) < debounce_sec:
        return True

    return False


def mark_session_as_checked(session_id: str | None) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache = load_session_cache()
        now = time.time()
        cache["last_check_time"] = now

        if session_id:
            sessions = cache.get("sessions", {})
            # Prune sessions older than 24 hours
            sessions = {sid: ts for sid, ts in sessions.items() if (now - ts) < 86400}
            sessions[session_id] = now
            cache["sessions"] = sessions

        SESSION_CACHE_FILE.write_text(json.dumps(cache), encoding="utf-8")
    except Exception:
        pass


def run_git(args: list[str], cwd: pathlib.Path, timeout: float = 4.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding="utf-8",
        errors="replace",
    )


def is_git_repo(root: pathlib.Path) -> bool:
    if not (root / ".git").exists():
        return False
    try:
        res = run_git(["rev-parse", "--is-inside-work-tree"], cwd=root, timeout=2.0)
        return res.returncode == 0 and res.stdout.strip() == "true"
    except Exception:
        return False


def has_git_remote(root: pathlib.Path) -> bool:
    try:
        res = run_git(["remote"], cwd=root, timeout=2.0)
        return res.returncode == 0 and bool(res.stdout.strip())
    except Exception:
        return False


def is_working_tree_clean(root: pathlib.Path) -> bool:
    try:
        res = run_git(["status", "--porcelain", "--untracked-files=no"], cwd=root, timeout=2.0)
        return res.returncode == 0 and res.stdout.strip() == ""
    except Exception:
        return True


def get_local_and_remote_sha(root: pathlib.Path) -> tuple[str, str]:
    local_sha = ""
    remote_sha = ""
    try:
        res = run_git(["rev-parse", "HEAD"], cwd=root, timeout=2.0)
        if res.returncode == 0:
            local_sha = res.stdout.strip()

        # Try tracking upstream branch first (@{u})
        res_u = run_git(["rev-parse", "@{u}"], cwd=root, timeout=2.0)
        if res_u.returncode == 0 and res_u.stdout.strip():
            remote_sha = res_u.stdout.strip()
        else:
            # Fallback to origin/main or origin/master
            res_main = run_git(["rev-parse", "origin/main"], cwd=root, timeout=2.0)
            if res_main.returncode == 0:
                remote_sha = res_main.stdout.strip()
            else:
                res_master = run_git(["rev-parse", "origin/master"], cwd=root, timeout=2.0)
                if res_master.returncode == 0:
                    remote_sha = res_master.stdout.strip()
    except Exception:
        pass
    return local_sha, remote_sha


def fetch_upstream(root: pathlib.Path, timeout: float = 3.0) -> bool:
    try:
        res = run_git(["fetch", "--quiet"], cwd=root, timeout=timeout)
        return res.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False


def sync_targets(root: pathlib.Path) -> bool:
    sync_script = root / "sync.sh"
    if not sync_script.exists():
        return False
    try:
        res = subprocess.run(
            [str(sync_script), "--fix"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60.0,
        )
        return res.returncode == 0
    except Exception:
        return False


def check_and_update_session(session_id: str | None = None, force: bool = False) -> dict[str, str | bool]:
    """Checks and updates repository once per session.
    
    Returns status dict:
      {"status": "updated" | "up_to_date" | "already_checked" | "locked" | "dirty_skipped" | "fetch_failed" | "disabled" | "no_git"}
    """
    if is_auto_update_disabled():
        return {"status": "disabled"}

    if not is_git_repo(ROOT) or not has_git_remote(ROOT):
        return {"status": "no_git"}

    if not force and is_session_already_checked(session_id):
        return {"status": "already_checked", "skipped": True}

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    lock_file_obj = None
    try:
        lock_file_obj = open(LOCK_FILE, "w")
        try:
            fcntl.flock(lock_file_obj, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (IOError, OSError):
            return {"status": "locked", "skipped": True}

        # Perform fetch (fail-open on network timeout / offline)
        fetch_ok = fetch_upstream(ROOT, timeout=3.0)
        mark_session_as_checked(session_id)

        if not fetch_ok:
            return {"status": "fetch_failed", "skipped": True}

        local_sha, remote_sha = get_local_and_remote_sha(ROOT)
        if not local_sha or not remote_sha:
            return {"status": "sha_error"}

        if local_sha == remote_sha:
            return {"status": "up_to_date", "sha": local_sha}

        # Remote has new changes
        if not is_working_tree_clean(ROOT):
            print(
                f"[unicli-hub] Remote update available ({local_sha[:7]} -> {remote_sha[:7]}), "
                "but local uncommitted changes exist. Skipping auto-pull.",
                file=sys.stderr,
            )
            return {"status": "dirty_skipped", "local": local_sha, "remote": remote_sha}

        print(
            f"[unicli-hub] Updating repository ({local_sha[:7]} -> {remote_sha[:7]})...",
            file=sys.stderr,
        )
        pull_res = run_git(["pull", "--ff-only", "--quiet"], cwd=ROOT, timeout=10.0)
        if pull_res.returncode != 0:
            print(
                f"[unicli-hub] Fast-forward update failed: {pull_res.stderr.strip()}",
                file=sys.stderr,
            )
            return {"status": "pull_failed", "error": pull_res.stderr}

        sync_ok = sync_targets(ROOT)
        if sync_ok:
            print(
                f"[unicli-hub] Successfully updated to {remote_sha[:7]} and synchronized all AI CLI targets.",
                file=sys.stderr,
            )
        return {"status": "updated", "from": local_sha, "to": remote_sha, "synced": sync_ok}

    finally:
        if lock_file_obj is not None:
            try:
                fcntl.flock(lock_file_obj, fcntl.LOCK_UN)
                lock_file_obj.close()
            except Exception:
                pass


def main() -> None:
    force = False
    session_id = None
    for arg in sys.argv[1:]:
        if arg in ("--force", "-f", "--fix"):
            force = True
        elif arg.startswith("--session-id="):
            session_id = arg.split("=", 1)[1]

    res = check_and_update_session(session_id=session_id, force=force)
    if "--json" in sys.argv:
        print(json.dumps(res, indent=2))
    elif res.get("status") == "updated":
        print(f"Updated: {res.get('from', '')[:7]} -> {res.get('to', '')[:7]}")
    elif res.get("status") == "up_to_date":
        print(f"Already up to date ({str(res.get('sha', ''))[:7]})")
    elif res.get("status") == "already_checked":
        print("Already checked for this session.")
    elif res.get("status") == "dirty_skipped":
        print("Update available but skipped due to uncommitted changes.")


if __name__ == "__main__":
    main()
