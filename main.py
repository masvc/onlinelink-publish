import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from urllib.parse import quote

# 環境変数を読み込み
load_dotenv()

CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("ZOOM_ACCESS_TOKEN")

def get_authorization_url():
    """認証URLを生成"""
    redirect_uri = "http://localhost:3000/oauth/callback"
    
    auth_url = (
        f"https://zoom.us/oauth/authorize?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={redirect_uri}"
    )
    
    print("以下のURLをブラウザで開いて、認証してください:")
    print(auth_url)
    print("\nリダイレクト後のURLから 'code=' 以降の文字列をコピーしてください")

def get_access_token_from_code(auth_code):
    """認証コードからアクセストークンを取得"""
    url = "https://zoom.us/oauth/token"
    redirect_uri = "http://localhost:3000/oauth/callback"
    
    response = requests.post(
        url,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": redirect_uri
        }
    )
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ アクセストークン取得成功")
        print(f"\n以下を .env ファイルに追加してください:")
        print(f"ZOOM_ACCESS_TOKEN={token_data['access_token']}")
        print(f"ZOOM_REFRESH_TOKEN={token_data['refresh_token']}")
        return token_data
    else:
        print(f"❌ トークン取得エラー: {response.status_code}")
        print(response.text)
        return None

def create_meeting(topic, start_time, duration=30):
    """Zoomミーティングを作成"""
    if not ACCESS_TOKEN:
        print("❌ アクセストークンが設定されていません")
        get_authorization_url()
        return None
    
    url = "https://api.zoom.us/v2/users/me/meetings"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # ISO 8601フォーマットに変換
    if isinstance(start_time, datetime):
        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S")
    else:
        start_time_str = start_time
    
    data = {
        "topic": topic,
        "type": 2,
        "start_time": start_time_str,
        "duration": duration,
        "timezone": "Asia/Tokyo",
        "settings": {
            "host_video": True,
            "participant_video": True,
            "join_before_host": False,
            "mute_upon_entry": True,
            "auto_recording": "cloud"
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        meeting = response.json()
        print("\n✅ ミーティング作成成功!")
        print(f"📝 トピック: {meeting['topic']}")
        print(f"🔗 参加URL: {meeting['join_url']}")
        print(f"🆔 ミーティングID: {meeting['id']}")
        print(f"📅 開始時刻: {meeting['start_time']}")
        print(f"⏱️  所要時間: {meeting['duration']}分")
        return meeting
    else:
        print(f"\n❌ ミーティング作成エラー: {response.status_code}")
        print(response.text)
        return None

def create_google_calendar_url(meeting, attendee_email=None):
    """Googleカレンダー追加用URLを生成"""
    # 日時をパース
    start_time = datetime.fromisoformat(meeting['start_time'].replace('Z', '+00:00'))
    end_time = start_time + timedelta(minutes=meeting['duration'])
    
    # 日本時間で表示用
    start_time_jst = start_time.astimezone()
    
    # カレンダーイベントの詳細
    description = f"""Zoomオンライン商談

参加URL: {meeting['join_url']}
ミーティングID: {meeting['id']}

※ 上記URLより参加してください
"""
    
    # Googleカレンダー追加URL生成
    calendar_url = (
        "https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={quote(meeting['topic'])}"
        f"&dates={start_time.strftime('%Y%m%dT%H%M%S')}Z/{end_time.strftime('%Y%m%dT%H%M%S')}Z"
        f"&details={quote(description)}"
        f"&location={quote('Online (Zoom)')}"
    )
    
    # 招待者がいる場合
    if attendee_email:
        calendar_url += f"&add={quote(attendee_email)}"
    
    print(f"\n📅 Googleカレンダーに追加:")
    print(f"   日時: {start_time_jst.strftime('%Y/%m/%d %H:%M')} ({meeting['duration']}分)")
    if attendee_email:
        print(f"   招待: {attendee_email}")
    print(f"\n   以下のURLをクリックしてカレンダーに追加してください:")
    print(f"   {calendar_url}")
    
    return calendar_url

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Zoom API + Googleカレンダー連携テスト")
    print("=" * 60)
    
    # 初回セットアップモード
    if not ACCESS_TOKEN:
        print("\n🔧 初回セットアップ:")
        get_authorization_url()
        print("\n2. ブラウザで認証後、codeを入力してください:")
        auth_code = input("Authorization Code: ").strip()
        
        if auth_code:
            token_data = get_access_token_from_code(auth_code)
            if token_data:
                print("\n✅ セットアップ完了!")
                print("もう一度スクリプトを実行してください")
    else:
        # ミーティング作成
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        
        meeting = create_meeting(
            topic="【テスト】吉田様との商談",
            start_time=start_time,
            duration=30
        )
        
        if meeting:
            # Googleカレンダー追加URL生成
            calendar_url = create_google_calendar_url(
                meeting,
                attendee_email="m.yoshida553@gmail.com"
            )
            
            print("\n" + "=" * 60)
            print("💡 次のステップ:")
            print("1. ✅ Zoomミーティングが作成されました")
            print("2. 📅 上記URLをクリックしてGoogleカレンダーに追加")
            print("3. ✉️  必要に応じて招待メールを手動送信")
            print("=" * 60)