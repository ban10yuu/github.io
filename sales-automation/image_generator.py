"""営業自動化ツール - イメージ画像生成モジュール
Google Gemini (Imagen) APIで業種別イメージ画像を生成する
"""
import os
import base64
import requests
from config import GEMINI_API_KEY, IMAGE_DIR

# 業種別の画像生成プロンプト
CATEGORY_PROMPTS = {
    "歯科医院": [
        "Modern dental clinic promotional video thumbnail, professional dentist explaining treatment, clean bright clinic interior, Japanese style, high quality",
        "Dental clinic staff training video scene, team meeting in clinic, professional medical environment, Japanese",
        "Dental clinic recruitment video, young dentist working, modern equipment, welcoming atmosphere",
    ],
    "病院": [
        "Hospital promotional video thumbnail, professional medical staff, modern hospital interior, Japanese healthcare",
        "Medical training video scene, doctors in conference room, professional healthcare education",
        "Hospital recruitment video, diverse medical team, state-of-the-art facility, welcoming environment",
    ],
    "クリニック": [
        "Small clinic promotional video, friendly doctor consultation, warm interior design, Japanese medical office",
        "Clinic staff training video, medical team learning, professional development, healthcare",
        "Clinic recruitment video, medical professional at work, modern small clinic",
    ],
    "工務店": [
        "Construction company promotional video, beautiful house exterior, Japanese residential architecture",
        "Construction worker training video, safety training scene, professional worksite",
        "Construction company recruitment, skilled craftsman at work, Japanese traditional carpentry",
    ],
    "不動産": [
        "Real estate company promotional video, luxury property showcase, Japanese modern apartment",
        "Real estate agent training video, professional consultation scene, office environment",
        "Real estate recruitment video, young professional showing property, modern office",
    ],
    "介護施設": [
        "Nursing care facility promotional video, caring staff with elderly, warm Japanese facility",
        "Care worker training video, professional caregiving demonstration, compassionate environment",
        "Nursing care recruitment, young caregiver helping elderly, bright modern facility",
    ],
    "default": [
        "Corporate promotional video thumbnail, professional business meeting, modern Japanese office",
        "Company training video, staff development session, professional environment",
        "Corporate recruitment video, diverse team collaboration, modern workplace",
    ],
}


def generate_image(prompt, filename):
    """Gemini APIで画像を生成して保存する

    Args:
        prompt: 画像生成プロンプト
        filename: 保存ファイル名

    Returns:
        保存したファイルパス、失敗時はNone
    """
    os.makedirs(IMAGE_DIR, exist_ok=True)
    filepath = os.path.join(IMAGE_DIR, filename)

    # 既に生成済みならスキップ
    if os.path.exists(filepath):
        return filepath

    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "16:9",
        },
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        if "predictions" in data and data["predictions"]:
            img_bytes = base64.b64decode(data["predictions"][0]["bytesBase64Encoded"])
            with open(filepath, "wb") as f:
                f.write(img_bytes)
            print(f"  画像生成完了: {filename}")
            return filepath
        else:
            print(f"  画像生成失敗: レスポンスにpredictionsなし")
            return None

    except Exception as e:
        print(f"  画像生成エラー: {e}")
        return None


def generate_images_for_category(category, company_name=None):
    """業種に応じたイメージ画像を生成する

    Args:
        category: 業種名
        company_name: 企業名（ファイル名に使用）

    Returns:
        生成された画像ファイルパスのリスト
    """
    prompts = CATEGORY_PROMPTS.get(category, CATEGORY_PROMPTS["default"])
    safe_name = (company_name or category).replace(" ", "_").replace("/", "_")

    images = []
    for i, prompt in enumerate(prompts):
        filename = f"{safe_name}_{i+1}.png"
        path = generate_image(prompt, filename)
        if path:
            images.append(path)

    return images


if __name__ == "__main__":
    print("テスト: 歯科医院の画像生成")
    images = generate_images_for_category("歯科医院", "テスト歯科")
    print(f"生成された画像: {images}")
