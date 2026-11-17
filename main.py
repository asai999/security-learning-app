from fastapi.responses import FileResponse
import sqlite3
from pathlib import Path
from contextlib import closing

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal

app = FastAPI()

DB_PATH = Path(__file__).with_name("security_learning.db")


# データベース接続
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# 回答データの定義
class AnswerRequest(BaseModel):
    answer: Literal["A", "B", "C", "D"]


# 問題取得API
@app.get("/questions/{question_id}")
def get_question(question_id: int):

    with closing(get_connection()) as conn:
        question = conn.execute(
            "SELECT * FROM questions WHERE id = ?",
            (question_id,)
        ).fetchone()

    if question is None:
        raise HTTPException(404, "問題が見つかりません")

    return {
        "id": question["id"],
        "title": question["title"],
        "question": question["question"],
        "choices": {
            "A": question["choice_a"],
            "B": question["choice_b"],
            "C": question["choice_c"],
            "D": question["choice_d"]
        }
    }


# 回答・採点API
@app.post("/questions/{question_id}/answer")
def submit_answer(question_id: int, request: AnswerRequest):

    with closing(get_connection()) as conn:
        question = conn.execute(
            "SELECT * FROM questions WHERE id = ?",
            (question_id,)
        ).fetchone()

        if question is None:
            raise HTTPException(404, "問題が見つかりません")

        is_correct = request.answer == question["correct_answer"]

        # 回答履歴を保存
        conn.execute("""
            INSERT INTO submissions
            (question_id, submitted_answer, is_correct)
            VALUES (?, ?, ?)
        """, (
            question_id,
            request.answer,
            int(is_correct)
        ))

        conn.commit()

    return {
        "is_correct": is_correct,
        "correct_answer": question["correct_answer"],
        "explanation": question["explanation"]
    }


# 回答履歴取得API
@app.get("/history")
def get_history():

    with closing(get_connection()) as conn:
        rows = conn.execute("""
            SELECT * FROM submissions
            ORDER BY id DESC
            LIMIT 20
        """).fetchall()

    return [
        {**dict(row), "is_correct": bool(row["is_correct"])}
        for row in rows
    ]

@app.get("/")
def home():
    return FileResponse(
        Path(__file__).with_name("index.html")
    )