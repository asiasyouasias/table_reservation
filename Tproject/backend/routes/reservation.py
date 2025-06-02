import sqlite3, re
from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
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
    print("세션 전체:", dict(session))
    if "email" not in session:
        return jsonify({"success": False, "message": "로그인이 필요합니다"}), 401

    data = request.get_json()


    # 입력 값 체크
    required_fields = ["date", "meal", "table_id", "name", "phone", "credit", "quantity"]
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "message": f"{field} 필수 입력값입니다."}), 400

    user = session["email"]
    date = data.get("date")
    meal = data.get("meal")
    table_id = data.get("table_id")
    name = data.get("name")
    phone = data.get("phone")
    credit = data.get("credit")
    quantity = data.get("quantity")


    # 유효성 검사
    if not is_valid_phone(phone):
        return jsonify({"success": False, "message": "전화번호 형식이 올바르지 않습니다"}), 400
    if not is_valid_credit(credit):
        return jsonify({"success": False, "message": "카드번호 형식이 올바르지 않습니다"}), 400
    

    # 날짜 형식 검사
    try:
        res_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"success": False, "message": "날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)"}), 400


    # 30일 초과 예약 차단
    today = datetime.today().date()
    if res_date > today + timedelta(days=30):
        return jsonify({"success": False, "message": "예약은 오늘로부터 30일 이내 날짜만 가능합니다."}), 400


    try:
        conn = sqlite3.connect(RES_DB)
        conn.execute("ATTACH DATABASE ? AS users_db", (USER_DB,))
        conn.execute("ATTACH DATABASE ? AS tables_db", (TABLE_DB,))
        c = conn.cursor()


        # 사용자 id 조회
        c.execute("SELECT id FROM users_db.users WHERE username = ?", (user,))
        user_row = c.fetchone()
        if not user_row:
            return jsonify({"success": False, "message": "해당 유저 없음"}), 400
        user_id = user_row[0]


        # 테이블 정보 조회
        c.execute("SELECT capacity FROM tables_db.tables WHERE id = ?", (table_id,))
        table_info = c.fetchone()
        if not table_info:
            return jsonify({"success": False, "message": "해당 테이블 없음"}), 400
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
            INSERT INTO reservations (user_id, table_id, date, meal, name, phone, credit, quantity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, table_id, date, meal, name, phone, credit, quantity))
        conn.commit()


    # DB 오류
    except sqlite3.Error as e:
        return jsonify({"success": False, "message": "DB 오류가 발생했습니다.", "error": str(e)}), 500


    finally:
        conn.close()

    return jsonify({"success": True, "message": "예약 성공!"})



# 예약 취소 기능
@reservation_bp.route("/api/reservations/cancel", methods=["POST"])
def cancel_reservation():
    if "email" not in session:
        return jsonify({"success": False, "message": "로그인이 필요합니다"}), 401

    data = request.get_json()
    table_id = data.get("table_id")
    date = data.get("date")
    meal = data.get("meal")


    # 입력값 확인
    if not table_id or not date or not meal:
        return jsonify({"success": False, "message": "table_id, date, meal 필수 입력값입니다."}), 400
    
    # 유효성 검사
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"success": False, "message": "날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)"}), 400


    user = session["email"]

    try:
        conn = sqlite3.connect(RES_DB)
        conn.execute("ATTACH DATABASE ? AS users_db", (USER_DB,))
        c = conn.cursor()


        # 사용자 id 조회
        c.execute("SELECT id FROM users_db.users WHERE username = ?", (user,))
        user_row = c.fetchone()
        if not user_row:
            return jsonify({"success": False, "message": "해당 유저 없음"}), 400
        user_id = user_row[0]

        
        # 예약 정보 조회
        c.execute("""
            SELECT id, date FROM reservations
            WHERE user_id = ? AND table_id = ? AND date = ? AND meal = ?
        """, (user_id, table_id, date, meal))
        row = c.fetchone()

        if not row:
            return jsonify({"success": False, "message": "예약을 찾을 수 없습니다."}), 404

        reservation_id, res_date_str = row
        today = datetime.today().date()
        res_date = datetime.strptime(res_date_str, "%Y-%m-%d").date()


        # 당일 취소 방지
        if res_date <= today:
            return jsonify({"success": False, "message": "당일 예약은 취소할 수 없습니다"}), 400


        # 예약 삭제
        c.execute("DELETE FROM reservations WHERE id = ?", (reservation_id,))
        conn.commit()
        conn.close()


    # DB 오류
    except sqlite3.Error as e:
        return jsonify({"success": False, "message": "DB 오류가 발생했습니다.", "error": str(e)}), 500
    
    finally:
        conn.close()
    
    return jsonify({"success": True, "message": "예약이 취소되었습니다."})

