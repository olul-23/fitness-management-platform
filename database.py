"""
database.py — SQLite 資料庫管理模組

負責建立資料表與提供 CRUD 操作。
本專案使用單檔 SQLite，零安裝、適合期末展示。

資料表設計：
    user_profile      使用者個人資料（單筆）
    menus             儲存的訓練菜單（多筆）
    menu_exercises    每份菜單包含的動作（與 menus 一對多）
    training_records  每次訓練的實際紀錄（每組動作一筆）
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
# SQLite 檔案路徑（與程式同資料夾）
# 用 Path 確保跨作業系統可用
DB_PATH = Path(__file__).parent / "fitness.db"


@contextmanager
def get_conn():
    """Context manager — 自動 commit、自動關閉連線。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # 讓 query 結果可以用欄位名稱存取（像 dict）
    conn.execute("PRAGMA foreign_keys = ON") # 啟用 foreign key 約束（SQLite 預設是關閉的）
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """初始化所有資料表（若已存在則略過）。"""
    with get_conn() as conn:
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                gender TEXT,
                age INTEGER,
                height REAL,
                weight REAL,
                level TEXT,
                updated_at TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS menus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                muscle_groups TEXT,
                source TEXT,
                created_at TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS menu_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                menu_id INTEGER NOT NULL,
                exercise_name TEXT NOT NULL,
                muscle_group TEXT,
                equipment TEXT,
                target_sets INTEGER,
                target_reps TEXT,
                notes TEXT,
                FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS training_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                exercise_name TEXT NOT NULL,
                muscle_group TEXT,
                sets INTEGER,
                reps INTEGER,
                weight REAL,
                menu_id INTEGER,
                source_menu_exercise_id INTEGER,
                notes TEXT,
                created_at TEXT
            )
        """)


# ============== 使用者資料 ==============
# 若資料已存在（id=1），則更新而不是新增
# 避免重複 user profile
def save_profile(gender: str, age: int, height: float, weight: float, level: str):
    """儲存或更新使用者個人資料（id 固定為 1，單一使用者）。"""
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO user_profile (id, gender, age, height, weight, level, updated_at)
            VALUES (1, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                gender=excluded.gender,
                age=excluded.age,
                height=excluded.height,
                weight=excluded.weight,
                level=excluded.level,
                updated_at=excluded.updated_at
        """, (gender, age, height, weight, level, datetime.now().isoformat(timespec="seconds")))


def get_profile() -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM user_profile WHERE id = 1").fetchone()
        return dict(row) if row else None


# ============== 訓練菜單 ==============
"""
建立訓練菜單（含動作清單）

流程：
1. 建立 menus 主表
2. 取得 menu_id
3. 寫入多筆 menu_exercises
"""

def create_menu(name: str, muscle_groups: list[str], source: str, exercises: list[dict]) -> int:
    """
    建立一份訓練菜單。
    exercises 為 dict 列表，每個 dict 至少含：
        name, muscle_group, equipment, sets, reps, notes
    回傳：新建立的 menu_id
    """
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO menus (name, muscle_groups, source, created_at)
            VALUES (?, ?, ?, ?)
        """, (name, ",".join(muscle_groups), source, datetime.now().isoformat(timespec="seconds")))
        menu_id = cur.lastrowid

        for ex in exercises:
            conn.execute("""
                INSERT INTO menu_exercises
                    (menu_id, exercise_name, muscle_group, equipment, target_sets, target_reps, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                menu_id,
                ex.get("name", ""),
                ex.get("muscle_group", ""),
                ex.get("equipment", ""),
                ex.get("sets", 3),
                ex.get("reps", "10"),
                ex.get("notes", ""),
            ))
        return menu_id


def list_menus() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM menus ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def get_menu_exercises(menu_id: int) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM menu_exercises WHERE menu_id = ? ORDER BY id",
            (menu_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def delete_menu(menu_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM menus WHERE id = ?", (menu_id,))


# ============== 訓練紀錄 ==============

def add_record(date: str, exercise_name: str, muscle_group: str,
               sets: int, reps: int, weight: float,
               menu_id: int | None = None,
               source_menu_exercise_id: int | None = None,
               notes: str = ""):
    """新增一筆訓練紀錄。"""
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO training_records
                (date, exercise_name, muscle_group, sets, reps, weight,
                 menu_id, source_menu_exercise_id, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (date, exercise_name, muscle_group, sets, reps, weight,
              menu_id, source_menu_exercise_id, notes,
              datetime.now().isoformat(timespec="seconds")))


def list_records(start_date: str | None = None, end_date: str | None = None) -> list[dict]:
    """查詢訓練紀錄。可選日期區間。"""
    query = "SELECT * FROM training_records"# 動態組 SQL（依照是否有日期條件）
    params = []
    if start_date and end_date:
        query += " WHERE date BETWEEN ? AND ?"
        params = [start_date, end_date]
    elif start_date:
        query += " WHERE date >= ?"
        params = [start_date]
    query += " ORDER BY date DESC, id DESC"

    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def delete_record(record_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM training_records WHERE id = ?", (record_id,))
