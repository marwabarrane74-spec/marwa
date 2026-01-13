from flask import Flask, request, jsonify
import sqlite3
import hashlib
import subprocess

app = Flask(__name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    hashed_password = hash_password(password)

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ✅ Requête paramétrée (anti SQL injection)
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hashed_password)
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@app.route("/ping", methods=["GET"])
def ping():
    host = request.args.get("host")

    # ✅ Suppression de la commande dangereuse
    if not host.isalnum():
        return "Invalid host", 400

    result = subprocess.run(
        ["ping", "-c", "1", host],
        capture_output=True,
        text=True
    )

    return result.stdout


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
