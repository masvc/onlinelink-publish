# Zoom 商談リンク自動作成システム

Zoom API を活用したオンライン商談リンク自動作成ツールテスト

## 機能

- ✅ Zoom OAuth 認証
- ✅ ミーティング自動作成
- ✅ Google カレンダー連携 URL 生成
- ✅ シンプルな Web UI

## セットアップ

### 1. 依存関係のインストール

```bash
uv sync
```

### 2. 環境変数の設定

`.env`ファイルを作成し、以下を設定:

```env
ZOOM_CLIENT_ID=your_client_id
ZOOM_CLIENT_SECRET=your_client_secret
ZOOM_ACCESS_TOKEN=your_access_token
ZOOM_REFRESH_TOKEN=your_refresh_token
```

### 3. 初回認証(必要な場合)

```bash
uv run main.py
```

表示された URL をブラウザで開き、認証コードを取得して`.env`に追加

## 使い方

### Web UI

```bash
uv run app.py
```

ブラウザで `http://localhost:5000` を開く

### CLI から直接実行

```bash
uv run main.py
```

## 技術スタック

- Python 3.13
- Flask (Web UI)
- Zoom API (OAuth 2.0)
- Google Calendar API 連携

## ディレクトリ構成

```
onlinelink-publish/
├── app.py              # Flask Webアプリ
├── main.py             # CLIスクリプト
├── templates/
│   └── index.html      # Web UI
├── .env                # 環境変数(gitignore)
├── pyproject.toml      # 依存関係
└── readme.md           # このファイル
```

## API 制限

- **プロプラン**: 20 リクエスト/秒
- **ユーザーあたり**: 100 ミーティング作成/日
