#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Refresh Token 발급 스크립트
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import json

# YouTube 업로드 권한
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_refresh_token():
    """Refresh Token 발급"""
    
    print("🔑 YouTube Refresh Token 발급 시작...\n")
    
    # CLIENT_ID와 CLIENT_SECRET 입력
    print("=" * 60)
    print("스토아 채널에서 사용 중인 OAuth 정보를 입력하세요:")
    print("=" * 60)
    
    client_id = input("\n1. YOUTUBE_CLIENT_ID 입력:\n   ").strip()
    client_secret = input("\n2. YOUTUBE_CLIENT_SECRET 입력:\n   ").strip()
    
    if not client_id or not client_secret:
        print("\n❌ CLIENT_ID 또는 CLIENT_SECRET가 비어있습니다!")
        return
    
    # OAuth 설정
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/"]
        }
    }
    
    print("\n" + "=" * 60)
    print("브라우저가 열리면:")
    print("1. yt.lucamagic.02@gmail.com 계정 선택")
    print("2. Future Now 채널 선택")
    print("3. 권한 허용")
    print("=" * 60)
    input("\n준비되셨으면 Enter를 눌러주세요...")
    
    try:
        # OAuth 플로우 시작
        flow = InstalledAppFlow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri='http://localhost:8080/'
        )
        
        # 브라우저 열기 (로컬 서버 8080 포트)
        credentials = flow.run_local_server(
            port=8080,
            prompt='consent',
            success_message='인증 완료! 이 창을 닫고 터미널로 돌아가세요.'
        )
        
        # Refresh Token 출력
        refresh_token = credentials.refresh_token
        
        if refresh_token:
            print("\n" + "=" * 60)
            print("✅ Refresh Token 발급 성공!")
            print("=" * 60)
            print("\n📋 아래 토큰을 복사하세요:\n")
            print(f"{refresh_token}\n")
            print("=" * 60)
            print("\n📝 GitHub Secrets에 추가:")
            print("   Name: YOUTUBE_REFRESH_TOKEN")
            print(f"   Value: {refresh_token}")
            print("=" * 60)
            
            # 파일로도 저장
            with open("refresh_token.txt", "w") as f:
                f.write(refresh_token)
            
            print("\n💾 토큰이 refresh_token.txt 파일에도 저장되었습니다.")
            
        else:
            print("\n❌ Refresh Token을 받지 못했습니다.")
            print("   다시 시도해주세요.")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("\n해결 방법:")
        print("1. CLIENT_ID와 CLIENT_SECRET 다시 확인")
        print("2. 브라우저에서 팝업 차단 해제")
        print("3. 방화벽에서 localhost:8080 허용")

if __name__ == "__main__":
    get_refresh_token()
