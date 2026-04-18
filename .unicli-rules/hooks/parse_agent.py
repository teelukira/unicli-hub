#!/usr/bin/env python3
import sys
import re
import json
import os

def parse_yml_list(text, key):
    """Extracts a bulleted list from YAML-like frontmatter."""
    pattern = rf"^{key}:\n((?:\s+-\s+.*\n?)*)"
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        return []
    items = match.group(1).strip().split('\n')
    return [i.strip().lstrip('-').strip() for i in items if i.strip()]

def parse_yml_map(text, key):
    """Extracts key-value pairs from YAML-like frontmatter."""
    pattern = rf"^{key}:\n((?:\s+[\w-]+:\s+.*\n?)*)"
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        return {}
    items = match.group(1).strip().split('\n')
    res = {}
    for i in items:
        if ':' in i:
            k, v = i.split(':', 1)
            res[k.strip()] = v.strip()
    return res

def parse_agent(path):
    if not os.path.exists(path):
        return {"error": "file not found"}
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Matches YAML frontmatter between --- and ---
    fm_match = re.search(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not fm_match:
        return {"body": content.strip()}
    
    fm_text = fm_match.group(1)
    body = fm_match.group(2).strip()
    
    # Extract scalar fields
    def get_scalar(key):
        m = re.search(rf"^{key}:\s*(.*)$", fm_text, re.MULTILINE)
        return m.group(1).strip() if m else ""

    res = {
        "name": get_scalar("name"),
        "description": get_scalar("description"),
        "model": get_scalar("model"),
        "tools": parse_yml_list(fm_text, "tools"),
        "aliases": parse_yml_map(fm_text, "aliases"),
        "body": body
    }
    return res

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided"}))
        sys.exit(1)
    
    try:
        data = parse_agent(sys.argv[1])
        print(json.dumps(data, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
