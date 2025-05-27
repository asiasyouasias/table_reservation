import sqlite3, re
from flask import Blueprint, request, jsonify, session
from datetime import datetime
from config import RESERVATIONS_DB, TABLES_DB, USERS_DB

reservation_bp = Blueprint("reservation", __name__)

# DB 파일 경로
RES_DB = RESERVATIONS_DB
TABLE_DB = TABLES_DB
USER_DB = USERS_DB

# 유효성
def is_valid_phone(phone):
    return re.fullmatch(r"\d{10,11}", phone) is not None

def is_valid_credit(credit):
    return re.fullmatch(r"\d{16}", credit) is not None


# 예약 기능
@reservation_bp.route("/api/reservations", methods=["POST"])
def make_reservation():
    if "username" not in session:
        return jsonify({"success": False, "message": "로그인이 필요합니다"}), 401

    data = request.get_json()
    user = session["username"]
    date = data.get("date")
    meal = data.get("meal")
    table_id = data.get("table_id")
    phone = data.get("phone")
    credit = data.get("credit")
    quantity = data.get("quantity")

    # 유효성 검사
    if not is_valid_phone(phone):
        return jsonify({"success": False, "message": "전화번호 형식이 올바르지 않습니다"}), 400
    if not is_valid_credit(credit):
        return jsonify({"success": False, "message": "카드번호 형식이 올바르지 않습니다"}), 400


    conn = sqlite3.connect(RES_DB)
    conn.execute("ATTACH DATABASE ? AS users_db", (USER_DB,))
    c = conn.cursor()

    c.execute("SELECT id FROM users_db.users WHERE username = ?", (user,))
    user_row = c.fetchone()
    if not user_row:
        return jsonify({"success": False, "message": "유저 없음"}), 400
    user_id = user_row[0]

    # 테이블 용량 조회
    conn.execute("ATTACH DATABASE ? AS tables_db", (TABLE_DB,))
    c.execute("SELECT capacity FROM tables_db.tables WHERE id = ?", (table_id,))
    table_info = c.fetchone()
    if not table_info:
        return jsonify({"success": False, "message": "해당 테이블이 존재하지 않습니다."}), 400

    capacity = table_info[0]

    # quantity가 capacity 초과하면 예약 불가
    if quantity > capacity:
        return jsonify({"success": False, "message": f"예약 인원이 테이블 수용 인원({capacity}명)을 초과할 수 없습니다."}), 400


    # 중복 예약 체크
    c.execute("""
        SELECT 1 FROM reservations
        WHERE table_id = ? AND date = ? AND meal = ?
    """, (table_id, date, meal))
    if c.fetchone():
        return jsonify({"success": False, "message": "이미 예약된 테이블입니다."}), 409


    # 예약 저장
    c.execute("""
        INSERT INTO reservations (user_id, table_id, date, meal, phone, credit, quantity)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, table_id, date, meal, phone, credit, quantity))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "예약 성공!"})


# 예약 취소 기능
@reservation_bp.route("/api/reservations/cancel", methods=["POST"])
def cancel_reservation():
    if "username" not in session:
        return jsonify({"success": False, "message": "로그인이 필요합니다"}), 401

    data = request.get_json()
    table_id = data.get("table_id")
    date = data.get("date")
    meal = data.get("meal")
    if not date or not meal:
        return jsonify({"success": False, "message": "date와 meal 파라미터가 필요합니다."}), 400

    user = session["username"]

    conn = sqlite3.connect(RES_DB)
    conn.execute("ATTACH DATABASE ? AS users_db", (USER_DB,))
    c = conn.cursor()

    c.execute("SELECT id FROM users_db.users WHERE username = ?", (user,))
    user_row = c.fetchone()
    if not user_row:
        conn.close()
        return jsonify({"success": False, "message": "유저 없음"}), 400
    user_id = user_row[0]

    # 예약 정보 조회 (예약 날짜, 예약한 사용자 id, 로그인한 사용자명)
    c.execute("""
        SELECT id, date FROM reservations
        WHERE user_id = ? AND table_id = ? AND date = ? AND meal = ?
    """, (user_id, table_id, date, meal))
    row = c.fetchone()

    if not row:
        conn.close()
        return jsonify({"success": False, "message": "예약을 찾을 수 없습니다."}), 404

    reservation_id, res_date_str = row
    today = datetime.today().date()
    res_date = datetime.strptime(res_date_str, "%Y-%m-%d").date()

    if res_date <= today:
        conn.close()
        return jsonify({"success": False, "message": "당일 예약은 취소할 수 없습니다"}), 400

    # 예약 삭제
    c.execute("DELETE FROM reservations WHERE id = ?", (reservation_id,))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "예약이 취소되었습니다."})

