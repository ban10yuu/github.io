"""営業自動化ツール - メール送信モジュール
Gmail API (OAuth2) でHTMLメール+画像添付を送信する
"""
import os
import base64
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from config import GMAIL_SENDER, GMAIL_CREDENTIALS_FILE, GMAIL_TOKEN_FILE

# Gmail APIのスコープ
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_gmail_service():
    """Gmail APIサービスを取得（OAuth2認証）"""
    creds = None

    # 保存済みトークンがあれば読み込み
    if os.path.exists(GMAIL_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_FILE, SCOPES)

    # トークンがないか期限切れの場合
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(GMAIL_CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"credentials.json が見つかりません: {GMAIL_CREDENTIALS_FILE}\n"
                    "Google Cloud Console からダウンロードしてください。"
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                GMAIL_CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # トークンを保存
        with open(GMAIL_TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        print("Gmail認証完了・トークン保存済み")

    return build("gmail", "v1", credentials=creds)


def create_message(to, subject, body_text, body_html=None, image_paths=None):
    """送信用メッセージを作成する

    Args:
        to: 送信先メールアドレス
        subject: 件名
        body_text: テキスト本文
        body_html: HTML本文（オプション）
        image_paths: 添付画像ファイルパスのリスト（オプション）

    Returns:
        Gmail API用のメッセージオブジェクト
    """
    msg = MIMEMultipart("mixed")
    msg["From"] = GMAIL_SENDER
    msg["To"] = to
    msg["Subject"] = subject

    # テキストとHTMLのマルチパート
    if body_html:
        alt_part = MIMEMultipart("alternative")
        alt_part.attach(MIMEText(body_text, "plain", "utf-8"))
        alt_part.attach(MIMEText(body_html, "html", "utf-8"))
        msg.attach(alt_part)
    else:
        msg.attach(MIMEText(body_text, "plain", "utf-8"))

    # 画像を添付
    if image_paths:
        for path in image_paths:
            if os.path.exists(path):
                filename = os.path.basename(path)
                mime_type, _ = mimetypes.guess_type(path)
                if mime_type and mime_type.startswith("image/"):
                    subtype = mime_type.split("/")[1]
                    with open(path, "rb") as f:
                        img = MIMEImage(f.read(), _subtype=subtype)
                    img.add_header("Content-Disposition", "attachment", filename=filename)
                    msg.attach(img)
                else:
                    with open(path, "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", "attachment", filename=filename)
                    msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


def send_email(to, subject, body_text, body_html=None, image_paths=None):
    """メールを送信する

    Args:
        to: 送信先メールアドレス
        subject: 件名
        body_text: テキスト本文
        body_html: HTML本文（オプション）
        image_paths: 添付画像ファイルパスのリスト（オプション）

    Returns:
        送信結果（成功時はメッセージID、失敗時はNone）
    """
    try:
        service = get_gmail_service()
        message = create_message(to, subject, body_text, body_html, image_paths)
        result = service.users().messages().send(
            userId="me", body=message
        ).execute()
        print(f"  メール送信完了: {to} (ID: {result['id']})")
        return result["id"]
    except Exception as e:
        print(f"  メール送信エラー ({to}): {e}")
        return None


if __name__ == "__main__":
    print("Gmail OAuth2 認証テスト")
    print(f"credentials.json: {'存在' if os.path.exists(GMAIL_CREDENTIALS_FILE) else '未配置'}")
    print(f"token.json: {'存在' if os.path.exists(GMAIL_TOKEN_FILE) else '未認証'}")
    if os.path.exists(GMAIL_CREDENTIALS_FILE):
        service = get_gmail_service()
        print("認証成功！Gmail送信可能です。")
    else:
        print("\ncredentials.json を配置してから再実行してください。")
        print("取得方法: Google Cloud Console → APIとサービス → 認証情報 → OAuthクライアントID → JSONダウンロード")
