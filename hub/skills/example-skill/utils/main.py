#!/usr/bin/env python3
"""
secrets_manager를 사용한 시크릿 키 로드 예제
"""
import sys
from secrets_manager import get_secret

def main():
    # .env.local 또는 시스템 환경 변수에서 EXAMPLE_API_KEY를 가져옵니다.
    api_key = get_secret("EXAMPLE_API_KEY")
    
    if api_key:
        # 시크릿 키 전체를 출력하지 않도록 주의 (앞뒤 일부만 출력)
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "****"
        print(f"✅ 성공: EXAMPLE_API_KEY를 찾았습니다. (값: {masked_key})")
    else:
        print("❌ 오류: EXAMPLE_API_KEY를 찾을 수 없습니다.")
        print("  해결 방법: 프로젝트 루트의 .env.local 파일에 다음을 추가하세요:")
        print("  EXAMPLE_API_KEY=your-secret-key-here")
        sys.exit(1)

if __name__ == "__main__":
    main()
