import os
import sys
from pathlib import Path
from typing import Optional

# python-dotenv is required: pip install python-dotenv
try:
    from dotenv import load_dotenv, find_dotenv
except ImportError:
    print("[WARN] python-dotenv not found. Environment variables must be set manually.", file=sys.stderr)
    load_dotenv = None

def initialize_secrets():
    """
    프로젝트 루트의 .env.local 또는 .env 파일을 찾아 로드합니다.
    디렉토리 구조를 위로 탐색하며 파일을 찾습니다.
    """
    if load_dotenv:
        # find_dotenv()는 현재 디렉토리부터 상위로 올라가며 .env 파일을 찾습니다.
        # .env.local을 우선적으로 찾기 위해 filename 인자를 명시적으로 사용합니다.
        env_path = find_dotenv('.env.local')
        if not env_path:
            env_path = find_dotenv('.env')
            
        if env_path:
            load_dotenv(env_path)
            # print(f"[INFO] Loaded environment from: {env_path}")
        else:
            pass # No .env file found, will fallback to actual environment variables

def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    설정된 환경 변수에서 값을 가져옵니다.
    """
    return os.environ.get(key, default)

# 모듈 로드 시 자동으로 초기화 수행
initialize_secrets()
