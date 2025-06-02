from flask import Flask
from flask_cors import CORS
from routes.auth import auth_bp
from routes.reservation import reservation_bp
from routes.table import table_bp

app = Flask(__name__)
app.secret_key = 'key'

# ✅ 세션 쿠키가 크로스사이트에서 동작하도록 설정
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = False  # ⚠️ HTTPS 환경이면 True로 바꾸기

# ✅ CORS 설정
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)


# ✅ 블루프린트 등록
app.register_blueprint(auth_bp)
app.register_blueprint(reservation_bp)
app.register_blueprint(table_bp)

if __name__ == "__main__":
    app.run(port=5050, debug=True)
