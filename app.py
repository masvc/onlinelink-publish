import os
from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("ZOOM_ACCESS_TOKEN")

def create_meeting(topic, start_time, duration=30):
    """Zoomミーティングを作成"""
    url = "https://api.zoom.us/v2/users/me/meetings"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "topic": topic,
        "type": 2,
        "start_time": start_time,
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
        return response.json()
    else:
        return None

def create_google_calendar_url(meeting, attendee_email):
    """Googleカレンダー追加用URLを生成"""
    start_time = datetime.fromisoformat(meeting['start_time'].replace('Z', '+00:00'))
    end_time = start_time + timedelta(minutes=meeting['duration'])
    
    description = f"""Zoomオンライン商談

参加URL: {meeting['join_url']}
ミーティングID: {meeting['id']}

※ 上記URLより参加してください
"""
    
    calendar_url = (
        "https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={quote(meeting['topic'])}"
        f"&dates={start_time.strftime('%Y%m%dT%H%M%S')}Z/{end_time.strftime('%Y%m%dT%H%M%S')}Z"
        f"&details={quote(description)}"
        f"&location={quote('Online (Zoom)')}"
        f"&add={quote(attendee_email)}"
    )
    
    return calendar_url

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-meeting', methods=['POST'])
def create_meeting_api():
    try:
        data = request.json
        
        # パラメータ取得
        meeting_name = data.get('meeting_name')
        attendee_email = data.get('attendee_email')
        meeting_date = data.get('meeting_date')
        meeting_time = data.get('meeting_time')
        duration = int(data.get('duration', 30))
        
        # 日時をISO形式に変換
        start_datetime = f"{meeting_date}T{meeting_time}:00"
        
        # Zoomミーティング作成
        meeting = create_meeting(meeting_name, start_datetime, duration)
        
        if not meeting:
            return jsonify({"error": "ミーティング作成に失敗しました"}), 500
        
        # Googleカレンダー追加URL生成
        calendar_url = create_google_calendar_url(meeting, attendee_email)
        
        return jsonify({
            "success": True,
            "meeting": {
                "topic": meeting['topic'],
                "join_url": meeting['join_url'],
                "meeting_id": meeting['id'],
                "start_time": meeting['start_time'],
                "duration": meeting['duration']
            },
            "calendar_url": calendar_url
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)