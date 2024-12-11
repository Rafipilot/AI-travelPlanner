
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin SDK
cred = credentials.Certificate("travex-76b7c-firebase-adminsdk-e5972-d297b4d236.json")
firebase_admin.initialize_app(cred)

app = Flask(__name__)
CORS(app)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        # Check if the user already exists
        user = auth.get_user_by_email(email)
        return jsonify({"message": "User already exists", "uid": user.uid}), 400
    except auth.UserNotFoundError:
        # Create new user
        user = auth.create_user(email=email, password=password)
        return jsonify({"message": "User created", "uid": user.uid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        # Since password validation is done client-side, we just fetch user info here
        user = auth.get_user_by_email(email)
        return jsonify({"message": f"Hello {user.email}", "uid": user.uid}), 200
    except auth.UserNotFoundError:
        return jsonify({"error": "User not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
