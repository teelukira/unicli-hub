#!/usr/bin/env python3
"""
pre_tool_use.py — Latest UniCLI-Hub Hook Entry Point.
Delegates to aidlc_unified_hook.py for project-specific governance.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

def main() -> None:
    # Read payload once
    try:
        raw_payload = sys.stdin.read()
        payload = json.loads(raw_payload)
    except Exception:
        print(json.dumps({"permission": "allow"}))
        return

    tool_name = payload.get("tool_name", "")
    
    # 1. Standard Guard Logic (from Latest Framework)
    # (Optional: we can keep the simple guard here or let aidlc_unified_hook handle it)
    # For now, let's delegate everything to aidlc_unified_hook to preserve state logic
    
    script_dir = Path(__file__).resolve().parent
    engine = script_dir / "aidlc_unified_hook.py"
    
    if not engine.exists():
        # Fallback if project engine is missing
        print(json.dumps({"permission": "allow"}))
        return

    # Call the project-specific logic engine
    proc = subprocess.Popen(
        [sys.executable, str(engine), "--phase", "before", "--tool", tool_name],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )
    
    stdout, stderr = proc.communicate(input=raw_payload)
    
    # Pass through stderr (for nudges/logs)
    if stderr:
        sys.stderr.write(stderr)
        sys.stderr.flush()
        
    # Pass through stdout (the JSON response)
    if stdout.strip():
        sys.stdout.write(stdout)
    else:
        # Fallback
        print(json.dumps({"permission": "allow"}))
        
    sys.exit(proc.returncode)

if __name__ == "__main__":
    main()
