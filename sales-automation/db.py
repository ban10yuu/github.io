"""営業自動化ツール - データベース管理モジュール
SQLiteで企業リスト・送信済み管理・重複排除を行う
"""
import sqlite3
import os
from datetime import datetime, date
from config import DB_PATH


def get_connection():
    """DB接続を取得"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """テーブルを初期化"""
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            area TEXT,
            address TEXT,
            phone TEXT,
            email TEXT,
            website TEXT,
            owner_name TEXT,
            description TEXT,
            source TEXT,
            collected_at TEXT DEFAULT (datetime('now', 'localtime')),
            UNIQUE(name, area)
        );

        CREATE TABLE IF NOT EXISTS sent_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL UNIQUE,
            email_to TEXT NOT NULL,
            subject TEXT,
            sent_at TEXT DEFAULT (datetime('now', 'localtime')),
            status TEXT DEFAULT 'sent',
            FOREIGN KEY (company_id) REFERENCES companies(id)
        );

        CREATE INDEX IF NOT EXISTS idx_companies_email ON companies(email);
        CREATE INDEX IF NOT EXISTS idx_companies_category ON companies(category);
        CREATE INDEX IF NOT EXISTS idx_companies_area ON companies(area);
        CREATE INDEX IF NOT EXISTS idx_sent_company ON sent_emails(company_id);
    """)
    conn.commit()
    conn.close()
    print("DB初期化完了")


def add_company(name, category, area, address=None, phone=None,
                email=None, website=None, owner_name=None,
                description=None, source=None):
    """企業を追加（重複はスキップ）"""
    conn = get_connection()
    try:
        conn.execute(
            """INSERT OR IGNORE INTO companies
               (name, category, area, address, phone, email, website, owner_name, description, source)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, category, area, address, phone, email, website,
             owner_name, description, source)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_unsent_companies(category=None, area=None, limit=None):
    """未送信の企業リストを取得（メールアドレスあり）"""
    conn = get_connection()
    query = """
        SELECT c.* FROM companies c
        LEFT JOIN sent_emails s ON c.id = s.company_id
        WHERE s.id IS NULL AND c.email IS NOT NULL AND c.email != ''
    """
    params = []
    if category:
        query += " AND c.category = ?"
        params.append(category)
    if area:
        query += " AND c.area = ?"
        params.append(area)
    if limit:
        query += " LIMIT ?"
        params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def is_already_sent(company_id):
    """送信済みかチェック（二重送信防止）"""
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM sent_emails WHERE company_id = ?",
        (company_id,)
    ).fetchone()
    conn.close()
    return row is not None


def record_sent(company_id, email_to, subject, status="sent"):
    """送信記録を追加"""
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO sent_emails (company_id, email_to, subject, status)
               VALUES (?, ?, ?, ?)""",
            (company_id, email_to, subject, status)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # 既に送信済み
        return False
    finally:
        conn.close()


def get_today_sent_count():
    """本日の送信件数を取得"""
    conn = get_connection()
    today = date.today().isoformat()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM sent_emails WHERE date(sent_at) = ?",
        (today,)
    ).fetchone()
    conn.close()
    return row["cnt"]


def get_stats():
    """統計情報を取得"""
    conn = get_connection()
    stats = {}
    stats["total_companies"] = conn.execute(
        "SELECT COUNT(*) FROM companies"
    ).fetchone()[0]
    stats["companies_with_email"] = conn.execute(
        "SELECT COUNT(*) FROM companies WHERE email IS NOT NULL AND email != ''"
    ).fetchone()[0]
    stats["total_sent"] = conn.execute(
        "SELECT COUNT(*) FROM sent_emails"
    ).fetchone()[0]
    stats["today_sent"] = get_today_sent_count()
    stats["unsent_with_email"] = conn.execute(
        """SELECT COUNT(*) FROM companies c
           LEFT JOIN sent_emails s ON c.id = s.company_id
           WHERE s.id IS NULL AND c.email IS NOT NULL AND c.email != ''"""
    ).fetchone()[0]

    # 業種別
    rows = conn.execute(
        "SELECT category, COUNT(*) as cnt FROM companies GROUP BY category ORDER BY cnt DESC"
    ).fetchall()
    stats["by_category"] = {r["category"]: r["cnt"] for r in rows}

    # エリア別
    rows = conn.execute(
        "SELECT area, COUNT(*) as cnt FROM companies GROUP BY area ORDER BY cnt DESC"
    ).fetchall()
    stats["by_area"] = {r["area"]: r["cnt"] for r in rows}

    conn.close()
    return stats


if __name__ == "__main__":
    init_db()
    print("Stats:", get_stats())
