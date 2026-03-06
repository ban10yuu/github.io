"""営業自動化ツール - 設定ファイル"""
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# === API Keys ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# === Gmail設定 ===
GMAIL_SENDER = os.getenv("GMAIL_SENDER", "")
GMAIL_CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials.json")
GMAIL_TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token.json")

# === データベース ===
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "sales.db")

# === 画像保存先 ===
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")

# === 営業対象エリア ===
TARGET_AREAS = [
    "奈良県天理市",
    "奈良県奈良市",
    "奈良県大和郡山市",
    "奈良県橿原市",
    "奈良県桜井市",
    "奈良県生駒市",
    "奈良県香芝市",
]

# === 営業対象業種 ===
TARGET_CATEGORIES = [
    "歯科医院",
    "病院",
    "クリニック",
    "工務店",
    "不動産",
    "介護施設",
    "学習塾",
    "美容室",
    "飲食店",
    "製造業",
]

# === 営業サービス内容 ===
SERVICES = [
    "社内教育・研修動画の制作",
    "マニュアルの動画化",
    "求人動画の制作",
    "企業YouTubeチャンネル制作・運営",
]

# === 依頼者情報 ===
SENDER_NAME = "番正 優児"
SENDER_TITLE = "フリーランス動画編集者・コンテンツプロデューサー"
SENDER_EMAIL = GMAIL_SENDER

# === 送信制限 ===
DAILY_SEND_LIMIT = 450  # Gmailの500件/日制限に余裕を持たせる

# === スクレイピング設定 ===
SEARCH_DELAY = (2, 5)  # リクエスト間の待機時間（秒）min, max
MAX_RESULTS_PER_SEARCH = 30  # 1回の検索で取得する最大件数
