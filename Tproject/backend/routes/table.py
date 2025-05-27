import sqlite3
from flask import Blueprint, request, jsonify, session
from config import TABLES_DB, RESERVATIONS_DB, USERS_DB

table_bp = Blueprint("table", __name__)

TABLE_DB = TABLES_DB
RES_DB = RESERVATIONS_DB
USER_DB = USERS_DB

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
            quantity INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(table_id) REFERENCES tables(id)
        )
    """)
    conn_res.commit()
    conn_res.close()


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


@table_bp.route("/api/tables", methods=["GET"])
def get_available_tables():
    if "username" not in session:
        return jsonify({"success": False, "message": "로그인이 필요합니다"}), 401
    
    date = request.args.get("date")
    meal = request.args.get("meal")
    if not date or not meal:
        return jsonify({"success": False, "message": "date와 meal 파라미터가 필요합니다."}), 400

    user = session["username"]

    conn = sqlite3.connect(RES_DB)
    conn.execute("ATTACH DATABASE ? AS tables_db", (TABLE_DB,))
    conn.execute("ATTACH DATABASE ? AS users_db", (USER_DB,))

    c = conn.cursor()

    c.execute("""
        SELECT t.id, t.location, t.capacity,
               CASE WHEN r.id IS NULL THEN 0 ELSE 1 END AS is_reserved,
               CASE WHEN r.user_id = u.id THEN 1 ELSE 0 END AS is_mine
        FROM tables_db.tables t
        LEFT JOIN reservations r
          ON t.id = r.table_id AND r.date = ? AND r.meal = ?
        LEFT JOIN users_db.users u
          ON u.username = ?
    """, (date, meal, user))

    tables = []
    for row in c.fetchall():
        tables.append({
            "id": row[0],
            "location": row[1],
            "capacity": row[2],
            "is_reserved": bool(row[3]), 
            "is_mine": bool(row[4])
        })
    conn.close()
    return jsonify(tables)