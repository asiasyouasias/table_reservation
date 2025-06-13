from flask import Flask, request, session
from flask_cors import CORS
from routes.auth import auth_bp
from routes.reservation import reservation_bp
from routes.table import table_bp



app = Flask(__name__)
app.secret_key = 'key'

@app.before_request
def log_session_cookie():
    print("💥 현재 요청에서 받은 쿠키:", request.cookies.get("session"))
    print("💥 Flask 세션 내부 이메일:", session.get("email"))




# CORS 설정
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

@app.before_request
def log_session_cookie():
    print("💥 현재 요청에서 받은 쿠키:", request.cookies.get("session"))
    print("💥 Flask 세션 내부 이메일:", session.get("email"))
    print("💥 Flask 세션 내부 전체:", dict(session))

# 세션 쿠키 설정
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False 
#app.config['SESSION_COOKIE_DOMAIN'] = 'localhost' 

app.register_blueprint(auth_bp)
app.register_blueprint(reservation_bp)
app.register_blueprint(table_bp)



if __name__ == "__main__":
    app.run(port=5050, debug=True)