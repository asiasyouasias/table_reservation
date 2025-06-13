import sqlite3
from flask_cors import CORS
from flask import Blueprint, request, jsonify, session
from config import USERS_DB

auth_bp = Blueprint("auth", __name__)
CORS(auth_bp, supports_credentials=True, origins="http://localhost:3000")

# DB 파일 경로
DB_PATH = USERS_DB

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

# 회원 가입    
@auth_bp.route("/api/create-user", methods=["POST","OPTIONS"])
def create_user():
    if request.method == "OPTIONS":
        return '', 204
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # 입력값 체크
    if not email or not password:
        return jsonify({"success": False, "message": "아이디와 비밀번호는 필수 입력입니다."}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (email, password))
        conn.commit()
        return jsonify({"success": True, "message": "회원가입 성공!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "이미 존재하는 사용자입니다."})
    finally:
        conn.close()

# 로그인
@auth_bp.route("/api/login", methods=["POST", "OPTIONS"]) 
def login():
    if request.method == "OPTIONS": 
        return '', 204

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # 입력값 체크
    if not email or not password:
        return jsonify({"success": False, "message": "아이디와 비밀번호는 필수 입력입니다."}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (email,))
    row = c.fetchone()
    conn.close()

    if row and row[0] == password:
        session.clear()
        session["email"] = email
        session.modified = True
        return jsonify({"success": True, "message": "로그인 성공!", "user":{"email": email}})
    else:
        return jsonify({"success": False, "message": "아이디 또는 비밀번호 오류"}), 401

# 로그아웃
@auth_bp.route("/api/logout", methods=["POST","OPTIONS"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "로그아웃 성공!"})

# 로그인 사용자 확인
@auth_bp.route("/api/check-login", methods=["GET"])
def check_login():
    email = session.get("email")
    if email:
        return jsonify({"loggedIn": True, "username": email})
    else:
        return jsonify({"loggedIn": False}), 401