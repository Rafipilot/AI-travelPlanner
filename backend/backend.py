from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = "\xf0?a\x9a\\\xff\xd4;\x0c\xcbHi"  # Fetch from env
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()

    if user and user.password == password:  
        login_user(user)
        return jsonify({"message": "Login successful"}, {"user_data": user})
    return jsonify({"message": "Invalid username or password"}), 401

@app.route('/create_user', methods=['POST'])
def create_user():


    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    print(f"Received username: {username}")
    print(f"Received password: {password}")


    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "Username already exists"}), 400

    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@app.route('/dashboard', methods=['POST'])
def dashboard():
    return jsonify({"username": current_user.username})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"})

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
