import sqlite3
from flask import Blueprint, request, jsonify, session
from config import TABLES_DB, RESERVATIONS_DB, USERS_DB
from datetime import datetime

table_bp = Blueprint("table", __name__)


# DB 파일 경로
TABLE_DB = TABLES_DB
RES_DB = RESERVATIONS_DB
USER_DB = USERS_DB


# 서버 시작 시 DB 및 테이블 자동 생성
def init_db():
    conn_table = sqlite3.connect(TABLE_DB)
    c_table = conn_table.cursor()
    c_table.execute("""
        CREATE TABLE IF NOT EXISTS tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            capacity INTEGER NOT NULL
        )
    """)
    conn_table.commit()
    conn_table.close()

    conn_res = sqlite3.connect(RES_DB)
    c_res = conn_res.cursor()
    c_res.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            table_id INTEGER NOT NULL,
            date DATE NOT NULL,
            meal TEXT NOT NULL,
            phone TEXT NOT NULL,
            credit TEXT NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)
    c_res.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_reservation_unique
        ON reservations (table_id, date, meal)
    """)
    conn_res.commit()
    conn_res.close()


# 테이블 데이터
def seed_tables():
    conn_table = sqlite3.connect(TABLE_DB)
    c_table = conn_table.cursor()
    c_table.execute("SELECT COUNT(*) FROM tables")
    count = c_table.fetchone()[0]
    if count == 0:
        tables = [
            ("window", 2),
            ("window", 4),
            ("room", 4),
            ("room", 6),
            ("inside", 2),
            ("inside", 6),
        ]
        for loc, cap in tables:
            c_table.execute("INSERT INTO tables (location, capacity) VALUES (?, ?)", (loc, cap))
        conn_table.commit()
    conn_table.close()


init_db()
seed_tables()


# 테이블 조회
@table_bp.route("/api/tables", methods=["GET"])
def get_available_tables():
    if "username" not in session:
        return jsonify({"success": False, "message": "로그인이 필요합니다"}), 401
    
    date = request.args.get("date")
    meal = request.args.get("meal")


    # 입력값 확인
    if not date or not meal:
        return jsonify({"success": False, "message": "date와 meal 파라미터가 필요합니다."}), 400
    
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"success": False, "message": "날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)"}), 400

    user = session["username"]


    try:
        conn = sqlite3.connect(RES_DB)
        conn.execute(f"ATTACH DATABASE '{TABLE_DB}' AS tables_db")
        conn.execute(f"ATTACH DATABASE '{USER_DB}' AS users_db")
        c = conn.cursor()


        # 사용자 id 조회
        c.execute("SELECT id FROM users_db.users WHERE username = ?", (user,))
        user_row = c.fetchone()
        if not user_row:
            conn.close()
            return jsonify({"success": False, "message": "유저 정보 없음"}), 400
        user_id = user_row[0]


        # 테이블 예약 상태 조회
        c.execute("""
            SELECT t.id, t.location, t.capacity,
                   CASE WHEN r.id IS NULL THEN 0 ELSE 1 END AS is_reserved,
                   CASE WHEN r.user_id = ? THEN 1 ELSE 0 END AS is_mine
            FROM tables_db.tables t
            LEFT JOIN reservations r
              ON t.id = r.table_id AND r.date = ? AND r.meal = ?
        """, (user_id, date, meal))


        tables = []
        for row in c.fetchall():
            tables.append({
                "id": row[0],
                "location": row[1],
                "capacity": row[2],
                "is_reserved": bool(row[3]), # 예약 상태
                "is_mine": bool(row[4]) # 내가 한 예약 여부
            })

        return jsonify(tables)
    
    except sqlite3.Error as e:
        return jsonify({"success": False, "message": "DB 오류 발생", "error": str(e)}), 500

    finally:
        conn.close()