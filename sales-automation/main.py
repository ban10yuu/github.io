#!/usr/bin/env python3
"""営業自動化ツール - メインCLI
奈良県内の企業に動画制作サービスの営業メールを自動送信する

使い方:
    python main.py collect --area 天理市 --category 歯科医院
    python main.py preview
    python main.py dryrun
    python main.py send --count 5
    python main.py stats
"""
import argparse
import sys
import time
from db import init_db, get_unsent_companies, is_already_sent, record_sent, get_today_sent_count, get_stats
from scraper import collect_companies
from email_generator import generate_email
from image_generator import generate_images_for_category
from mailer import send_email
from config import TARGET_AREAS, TARGET_CATEGORIES, DAILY_SEND_LIMIT


def cmd_collect(args):
    """企業リストを収集する"""
    init_db()

    areas = [f"奈良県{args.area}"] if args.area else TARGET_AREAS
    categories = [args.category] if args.category else TARGET_CATEGORIES

    total = 0
    for area in areas:
        for category in categories:
            count = collect_companies(area, category, max_results=args.max)
            total += count

    print(f"\n合計 {total}件 を新規収集しました")
    _show_stats()


def cmd_preview(args):
    """収集済み企業のプレビュー"""
    init_db()
    companies = get_unsent_companies(
        category=args.category,
        area=f"奈良県{args.area}" if args.area else None,
        limit=args.limit or 20
    )

    if not companies:
        print("未送信の企業（メールアドレスあり）がありません。")
        print("まず `python main.py collect` で企業を収集してください。")
        return

    print(f"\n=== 未送信企業一覧（{len(companies)}件）===\n")
    for i, c in enumerate(companies, 1):
        owner = c.get("owner_name") or "不明"
        print(f"  {i}. {c['name']} ({c['category']})")
        print(f"     エリア: {c['area']} / 代表者: {owner}")
        print(f"     メール: {c['email']} / Web: {c.get('website', 'なし')}")
        print()


def cmd_dryrun(args):
    """サンプル1件でドライラン（送信はしない）"""
    init_db()
    companies = get_unsent_companies(limit=1)

    if not companies:
        print("未送信の企業がありません。まず collect してください。")
        return

    company = companies[0]
    print(f"\n=== ドライラン: {company['name']} ===\n")
    print(f"宛先: {company['email']}")
    print(f"業種: {company['category']}")
    print(f"エリア: {company['area']}")
    print(f"代表者: {company.get('owner_name', '不明')}")
    print(f"Web: {company.get('website', 'なし')}")

    # メール文面を生成
    print("\n--- メール文面生成中... ---")
    email_content = generate_email(company)
    if not email_content:
        print("メール生成に失敗しました。Anthropic APIキーを確認してください。")
        return

    print(f"\n件名: {email_content['subject']}")
    print(f"\n{email_content['body_text']}")

    # 画像生成
    print("\n--- イメージ画像生成中... ---")
    images = generate_images_for_category(company["category"], company["name"])
    if images:
        print(f"生成画像: {len(images)}枚")
        for img in images:
            print(f"  - {img}")
    else:
        print("画像生成をスキップ（APIキー未設定 or エラー）")

    print("\n=== ドライラン完了 ===")
    print("この内容でよければ `python main.py send --count 5` で送信を開始できます。")

    return email_content, images


def cmd_send(args):
    """メールを送信する"""
    init_db()

    # 本日の送信上限チェック
    today_count = get_today_sent_count()
    remaining = DAILY_SEND_LIMIT - today_count
    if remaining <= 0:
        print(f"本日の送信上限（{DAILY_SEND_LIMIT}件）に達しています。明日再実行してください。")
        return

    count = min(args.count, remaining)
    companies = get_unsent_companies(
        category=args.category,
        area=f"奈良県{args.area}" if args.area else None,
        limit=count
    )

    if not companies:
        print("未送信の企業がありません。")
        return

    print(f"\n=== {len(companies)}件にメール送信開始 ===")
    print(f"（本日の送信済み: {today_count}件 / 上限: {DAILY_SEND_LIMIT}件）\n")

    # 初回確認
    if not args.yes:
        print(f"送信先一覧:")
        for i, c in enumerate(companies, 1):
            print(f"  {i}. {c['name']} <{c['email']}>")
        print()
        confirm = input("これでいいですね？ (y/N): ").strip().lower()
        if confirm != "y":
            print("送信をキャンセルしました。")
            return

    sent = 0
    errors = 0

    for i, company in enumerate(companies, 1):
        print(f"\n[{i}/{len(companies)}] {company['name']} ({company['email']})")

        # 二重送信防止チェック
        if is_already_sent(company["id"]):
            print("  → スキップ（送信済み）")
            continue

        # メール文面生成
        print("  メール生成中...")
        email_content = generate_email(company)
        if not email_content:
            print("  → メール生成失敗、スキップ")
            errors += 1
            continue

        # 画像生成
        print("  画像生成中...")
        images = generate_images_for_category(company["category"], company["name"])

        # メール送信
        print("  送信中...")
        result = send_email(
            to=company["email"],
            subject=email_content["subject"],
            body_text=email_content["body_text"],
            body_html=email_content["body_html"],
            image_paths=images if images else None,
        )

        if result:
            record_sent(company["id"], company["email"], email_content["subject"])
            sent += 1
            print(f"  → 送信成功")
        else:
            errors += 1
            print(f"  → 送信失敗")

        # 送信間隔（Gmail制限対策）
        if i < len(companies):
            time.sleep(3)

    print(f"\n=== 送信完了: 成功 {sent}件 / エラー {errors}件 ===")
    _show_stats()


def cmd_stats(args):
    """統計情報を表示"""
    init_db()
    _show_stats()


def _show_stats():
    """統計表示（内部関数）"""
    stats = get_stats()
    print(f"\n=== 統計 ===")
    print(f"  収集企業数: {stats['total_companies']}")
    print(f"  メールあり: {stats['companies_with_email']}")
    print(f"  送信済み:   {stats['total_sent']}")
    print(f"  本日送信:   {stats['today_sent']}")
    print(f"  未送信残:   {stats['unsent_with_email']}")

    if stats["by_category"]:
        print(f"\n  【業種別】")
        for cat, cnt in stats["by_category"].items():
            print(f"    {cat}: {cnt}件")

    if stats["by_area"]:
        print(f"\n  【エリア別】")
        for area, cnt in stats["by_area"].items():
            print(f"    {area}: {cnt}件")


def main():
    parser = argparse.ArgumentParser(
        description="営業自動化ツール - 奈良県内企業への動画制作サービス営業メール自動送信"
    )
    subparsers = parser.add_subparsers(dest="command", help="コマンド")

    # collect
    p_collect = subparsers.add_parser("collect", help="企業リストを収集")
    p_collect.add_argument("--area", help="エリア（例: 天理市）")
    p_collect.add_argument("--category", help="業種（例: 歯科医院）")
    p_collect.add_argument("--max", type=int, default=30, help="最大取得数")
    p_collect.set_defaults(func=cmd_collect)

    # preview
    p_preview = subparsers.add_parser("preview", help="収集済み企業のプレビュー")
    p_preview.add_argument("--area", help="エリアでフィルタ")
    p_preview.add_argument("--category", help="業種でフィルタ")
    p_preview.add_argument("--limit", type=int, help="表示件数")
    p_preview.set_defaults(func=cmd_preview)

    # dryrun
    p_dryrun = subparsers.add_parser("dryrun", help="サンプル1件でテスト（送信なし）")
    p_dryrun.set_defaults(func=cmd_dryrun)

    # send
    p_send = subparsers.add_parser("send", help="メール送信")
    p_send.add_argument("--count", type=int, default=5, help="送信件数")
    p_send.add_argument("--area", help="エリアでフィルタ")
    p_send.add_argument("--category", help="業種でフィルタ")
    p_send.add_argument("--yes", "-y", action="store_true", help="確認をスキップ")
    p_send.set_defaults(func=cmd_send)

    # stats
    p_stats = subparsers.add_parser("stats", help="統計情報")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
