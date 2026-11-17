
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("security_learning.db")

conn = sqlite3.connect(DB_PATH)

try:
    # 問題テーブル
    conn.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            question TEXT NOT NULL,
            choice_a TEXT NOT NULL,
            choice_b TEXT NOT NULL,
            choice_c TEXT NOT NULL,
            choice_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT NOT NULL
        )
    """)

    # 回答履歴テーブル
    conn.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY,
            question_id INTEGER NOT NULL,
            submitted_answer TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
    """)

    # 最初の問題を登録
    conn.execute("""
        INSERT OR IGNORE INTO questions
        (id, title, question,
         choice_a, choice_b, choice_c, choice_d,
         correct_answer, explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        1,
        "SQLインジェクション",
        "SQLインジェクションの主な対策は？",
        "SQL文を短くする",
        "パラメータ化クエリを使用する",
        "DBを再起動する",
        "テーブル名を変更する",
        "B",
        "パラメータ化クエリでSQL文と入力データを分離します。"
    ))

    conn.commit()
finally:
    conn.close()

print("データベースの初期化が完了しました")
