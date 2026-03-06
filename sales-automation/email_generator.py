"""営業自動化ツール - メール文面生成モジュール
Claude APIを使って企業ごとにパーソナライズされた営業メールを生成する
"""
import anthropic
from config import ANTHROPIC_API_KEY, SENDER_NAME, SENDER_TITLE, SERVICES


def generate_email(company):
    """企業情報に基づいてパーソナライズされた営業メールを生成する

    Args:
        company: dict with keys: name, category, area, owner_name, website, description

    Returns:
        dict with keys: subject, body_text, body_html
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # 宛名の設定
    if company.get("owner_name"):
        addressee = f"{company['owner_name']}様"
    else:
        addressee = "ご担当者様"

    services_text = "\n".join(f"・{s}" for s in SERVICES)

    prompt = f"""あなたは営業メールのライターです。以下の情報に基づいて、動画制作サービスの営業メールを作成してください。

【送信者情報】
名前: {SENDER_NAME}
肩書き: {SENDER_TITLE}

【送信先企業情報】
企業名: {company['name']}
業種: {company.get('category', '不明')}
エリア: {company.get('area', '奈良県')}
宛名: {addressee}
Webサイト: {company.get('website', 'なし')}

【提供サービス】
{services_text}

【メール作成ルール】
1. 件名は30文字以内で、開封したくなるような魅力的なものにする
2. 冒頭で相手の業種に合わせた具体的な課題に触れる
3. その課題を動画で解決できることを提案する
4. 業種に合わせたサービスを1-2つピックアップして具体的に提案する
5. 押し売り感を出さず、相手のメリットを強調する
6. 簡潔で読みやすく、全体300文字程度
7. 文末に送信者の署名を入れる

以下のJSON形式で出力してください（```json で囲まないでください）:
{{"subject": "件名", "body": "メール本文"}}
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        # レスポンスのパース
        text = response.content[0].text.strip()

        # JSON部分を抽出
        import json
        # ```jsonで囲まれている場合の対応
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        result = json.loads(text)

        # HTML版の本文を作成
        body_html = result["body"].replace("\n", "<br>\n")
        body_html = f"""<div style="font-family: 'Hiragino Sans', 'Yu Gothic', sans-serif;
                              font-size: 14px; line-height: 1.8; color: #333;">
            {body_html}
        </div>"""

        return {
            "subject": result["subject"],
            "body_text": result["body"],
            "body_html": body_html,
        }

    except Exception as e:
        print(f"  メール生成エラー ({company['name']}): {e}")
        return None


if __name__ == "__main__":
    sample = {
        "name": "テスト歯科医院",
        "category": "歯科医院",
        "area": "奈良県天理市",
        "owner_name": "山田太郎",
        "website": "https://example.com",
    }
    result = generate_email(sample)
    if result:
        print(f"件名: {result['subject']}")
        print(f"本文:\n{result['body_text']}")
