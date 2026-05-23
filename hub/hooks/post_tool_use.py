#!/usr/bin/env python3
"""
post_tool_use.py — Latest UniCLI-Hub Hook Entry Point.
Delegates to aidlc_unified_hook.py for project-specific governance.
"""

import json
import subprocess
import sys
from pathlib import Path

def main() -> None:
    try:
        raw_payload = sys.stdin.read()
        payload = json.loads(raw_payload)
    except Exception:
        print(json.dumps({"permission": "allow"}))
        return

    tool_name = payload.get("tool_name", "")
    script_dir = Path(__file__).resolve().parent
    engine = script_dir / "aidlc_unified_hook.py"
    
    if not engine.exists():
        print(json.dumps({"permission": "allow"}))
        return

    proc = subprocess.Popen(
        [sys.executable, str(engine), "--phase", "after", "--tool", tool_name],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )
    
    stdout, stderr = proc.communicate(input=raw_payload)
    
    if stderr:
        sys.stderr.write(stderr)
        sys.stderr.flush()
        
    if stdout.strip():
        sys.stdout.write(stdout)
    else:
        print(json.dumps({"permission": "allow"}))
        
    sys.exit(proc.returncode)

if __name__ == "__main__":
    main()
