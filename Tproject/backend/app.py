from flask import Flask
from flask_cors import CORS
from routes.auth import auth_bp
from routes.reservation import reservation_bp
from routes.table import table_bp

app = Flask(__name__)
app.secret_key = 'key'
CORS(app, supports_credentials=True)

app.register_blueprint(auth_bp)
app.register_blueprint(reservation_bp)
app.register_blueprint(table_bp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)