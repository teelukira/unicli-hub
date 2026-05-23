import os
import sys
import fcntl
import subprocess


def main():
    lock_file = os.path.join(os.path.dirname(__file__), ".sync.lock")
    f = None
    try:
        f = open(lock_file, "w")
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (IOError, OSError):
            print("sync.sh is already running, skipping this instance.", file=sys.stderr)
            return 0

        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        sync_script = os.path.join(root, "sync.sh")
        print("Running sync.sh --fix with lock...", file=sys.stderr)
        try:
            result = subprocess.run([sync_script, "--fix"], cwd=root, timeout=60)
            return result.returncode
        except subprocess.TimeoutExpired:
            print("lock_sync: sync.sh --fix timed out after 60s", file=sys.stderr)
            return 1
    finally:
        if f is not None:
            try:
                f.close()
            except OSError:
                pass


if __name__ == "__main__":
    sys.exit(main())
