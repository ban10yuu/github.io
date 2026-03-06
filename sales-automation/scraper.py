"""営業自動化ツール - 企業リスト収集モジュール
DuckDuckGoで企業を検索し、Webサイトからメールアドレスを抽出する
"""
import re
import time
import random
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from config import SEARCH_DELAY, MAX_RESULTS_PER_SEARCH
from db import add_company

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en;q=0.9",
}

# メールアドレス抽出用の正規表現
EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE
)

# 除外するメールドメイン（共通サービス等）
EXCLUDED_DOMAINS = {
    "example.com", "sentry.io", "wixpress.com",
    "googleapis.com", "googleusercontent.com",
    "w3.org", "schema.org", "wordpress.org",
}


def search_duckduckgo(query, max_results=MAX_RESULTS_PER_SEARCH):
    """DuckDuckGo HTML版で検索してURLリストを返す"""
    url = "https://html.duckduckgo.com/html/"
    params = {"q": query}

    try:
        resp = requests.post(url, data=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  検索エラー: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    for link in soup.select(".result__a"):
        href = link.get("href", "")
        # DuckDuckGoのリダイレクトURLから実際のURLを抽出
        if "uddg=" in href:
            from urllib.parse import parse_qs, urlparse as up
            parsed = up(href)
            qs = parse_qs(parsed.query)
            if "uddg" in qs:
                href = qs["uddg"][0]

        if href and href.startswith("http"):
            # 検索エンジンや広告サイトを除外
            domain = urlparse(href).netloc
            if not any(x in domain for x in [
                "duckduckgo", "google", "bing", "yahoo",
                "facebook", "twitter", "instagram", "youtube",
                "tabelog", "hotpepper", "gnavi",
            ]):
                results.append({
                    "url": href,
                    "title": link.get_text(strip=True),
                })

        if len(results) >= max_results:
            break

    return results


def extract_emails_from_url(url, follow_contact=True):
    """URLからメールアドレスを抽出する"""
    emails = set()

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException:
        return emails

    # ページ内のメールアドレスを抽出
    page_text = soup.get_text()
    found = EMAIL_PATTERN.findall(page_text)
    for email in found:
        domain = email.split("@")[1].lower()
        if domain not in EXCLUDED_DOMAINS and not email.endswith(".png"):
            emails.add(email.lower())

    # mailto:リンクからも抽出
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.startswith("mailto:"):
            email = href.replace("mailto:", "").split("?")[0].strip()
            if EMAIL_PATTERN.match(email):
                domain = email.split("@")[1].lower()
                if domain not in EXCLUDED_DOMAINS:
                    emails.add(email.lower())

    # お問い合わせページも辿る
    if follow_contact and not emails:
        contact_links = []
        for a_tag in soup.find_all("a", href=True):
            text = a_tag.get_text(strip=True).lower()
            href = a_tag["href"].lower()
            if any(w in text or w in href for w in [
                "contact", "お問い合わせ", "問い合わせ",
                "mail", "メール", "info",
            ]):
                full_url = urljoin(url, a_tag["href"])
                if urlparse(full_url).netloc == urlparse(url).netloc:
                    contact_links.append(full_url)

        for contact_url in contact_links[:2]:
            time.sleep(random.uniform(1, 2))
            emails.update(extract_emails_from_url(contact_url, follow_contact=False))

    return emails


def extract_company_info(url, soup=None):
    """Webサイトから企業情報を抽出する"""
    info = {"website": url}

    if soup is None:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException:
            return info

    # 電話番号の抽出
    phone_pattern = re.compile(r"0\d{1,4}[-\s]?\d{1,4}[-\s]?\d{3,4}")
    text = soup.get_text()
    phones = phone_pattern.findall(text)
    if phones:
        info["phone"] = phones[0].strip()

    # 住所の抽出（奈良県を含むもの）
    address_pattern = re.compile(r"奈良県[^\s\n<]{5,50}")
    addresses = address_pattern.findall(text)
    if addresses:
        info["address"] = addresses[0].strip()

    # 代表者名の抽出
    owner_patterns = [
        re.compile(r"(?:院長|代表|代表取締役|理事長|オーナー|店長)[：:\s]*([^\s\n<]{2,10})"),
        re.compile(r"([^\s\n<]{2,6})\s*(?:院長|代表|代表取締役|理事長)"),
    ]
    for pattern in owner_patterns:
        match = pattern.search(text)
        if match:
            name = match.group(1).strip()
            # 明らかに人名でないものを除外
            if not any(x in name for x in ["株式", "有限", "医療", "法人", "について"]):
                info["owner_name"] = name
                break

    return info


def collect_companies(area, category, max_results=MAX_RESULTS_PER_SEARCH):
    """指定エリア・業種の企業を収集してDBに登録する"""
    print(f"\n=== {area} の {category} を収集中 ===")

    query = f"{area} {category}"
    results = search_duckduckgo(query, max_results)
    print(f"  検索結果: {len(results)}件")

    collected = 0
    for i, result in enumerate(results):
        url = result["url"]
        title = result["title"]
        print(f"  [{i+1}/{len(results)}] {title[:40]}...")

        # 企業名の推定（検索結果のタイトルから）
        company_name = title.split(" - ")[0].split("｜")[0].split("|")[0].strip()
        company_name = company_name[:50]  # 長すぎる場合は切り詰め

        if not company_name or len(company_name) < 2:
            continue

        # メールアドレスを抽出
        emails = extract_emails_from_url(url)

        # 企業情報を抽出
        info = extract_company_info(url)

        email = list(emails)[0] if emails else None

        added = add_company(
            name=company_name,
            category=category,
            area=area,
            address=info.get("address"),
            phone=info.get("phone"),
            email=email,
            website=url,
            owner_name=info.get("owner_name"),
            description=f"DuckDuckGo検索で収集 ({title[:60]})",
            source="duckduckgo",
        )

        if added:
            collected += 1
            status = f"メール: {email}" if email else "メールなし"
            print(f"    → 登録 ({status})")
        else:
            print(f"    → スキップ（登録済み）")

        # レート制限
        delay = random.uniform(*SEARCH_DELAY)
        time.sleep(delay)

    print(f"  収集完了: {collected}件を新規登録")
    return collected


if __name__ == "__main__":
    from db import init_db
    init_db()
    collect_companies("奈良県天理市", "歯科医院", max_results=5)
