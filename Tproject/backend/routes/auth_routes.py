import sqlite3
from flask import Flask, request, jsonify, session
from flask_cors import CORS

server = Flask(__name__)
CORS(server, supports_credentials=True)

server.secret_key = "key"

# DB 파일 경로
DB_PATH = "users.db"

# 서버 시작 시 DB 및 테이블 자동 생성
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()


# 로그인
@server.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()

    if row and row[0] == password:
        session["username"] = username
        return jsonify({"success": True, 
                        "message": "로그인 성공!"})
    else:
        return jsonify({"success": False, 
                        "message": "아이디 또는 비밀번호 오류"})
    

# 회원 가입    
@server.route("/api/create-user", methods=["POST"])
def create_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username, password))
        conn.commit()
        conn.close()

        return jsonify({"success": True,
                       "message": "회원가입 성공!"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False,
                        "message": "이미 존재하는 사용자입니다."})


# 로그아웃
@server.route("/api/logout", methods=["POST"])
def delete_user():
    session.clear()
    return jsonify({"success": True, "message": "로그아웃 성공!"})


# 로그인 사용자 확인
@server.route("/api/check-login", methods=["GET"])
def check_login():
    username = session.get("username")
    if username:
        return jsonify({"loggedIn": True, "username": username})
    else:
        return jsonify({"loggedIn": False})


if __name__ == "__main__":
    server.run(port=5000, debug=True)