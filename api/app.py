from flask import Flask, request, jsonify
import sqlite3
import subprocess
import hashlib
import os
import ast

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me")

# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hashed_password)
    )

    if cursor.fetchone():
        return jsonify({"status": "success", "user": username})

    return jsonify({"status": "error"}), 401

# ================= PING =================
@app.route("/ping", methods=["POST"])
def ping():
    host = request.json.get("host")

    if not host or ";" in host or "&" in host:
        return {"error": "Invalid host"}, 400

    result = subprocess.run(
        ["ping", "-c", "1", host],
        capture_output=True,
        text=True
    )

    return {"output": result.stdout}

# ================= COMPUTE =================
@app.route("/compute", methods=["POST"])
def compute():
    expression = request.json.get("expression")

    try:
        node = ast.parse(expression, mode="eval")
        result = eval(compile(node, "", "eval"), {"__builtins__": {}})
        return {"result": result}
    except:
        return {"error": "Invalid expression"}, 400

# ================= HASH =================
@app.route("/hash", methods=["POST"])
def hash_password():
    pwd = request.json.get("password")
    hashed = hashlib.sha256(pwd.encode()).hexdigest()
    return {"sha256": hashed}

# ================= HELLO =================
@app.route("/hello", methods=["GET"])
def hello():
    return {"message": "Secure DevSecOps API"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
