from flask import Flask, request, jsonify
import sqlite3
import subprocess
import hashlib
import os
import ast

app = Flask(__name__)

# ✅ Secret via variable d’environnement
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me")

# ===================== LOGIN SECURISÉ =====================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ✅ Requête préparée (anti SQL injection)
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hashed_password)
    )

    if cursor.fetchone():
        return jsonify({"status": "success", "user": username})

    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

# ===================== PING SECURISÉ =====================
@app.route("/ping", methods=["POST"])
def ping():
    host = request.json.get("host")

    # ✅ Validation simple IP/hostname
    if not host or ";" in host or "&" in host:
        return {"error": "Invalid host"}, 400

    result = subprocess.run(
        ["ping", "-c", "1", host],
        capture_output=True,
        text=True
    )

    return {"output": result.stdout}

# ===================== CALCUL SECURISÉ =====================
@app.route("/compute", methods=["POST"])
def compute():
    expression = request.json.get("expression")

    try:
        node = ast.parse(expression, mode="eval")
        result = eval(compile(node, "", "eval"), {"__builtins__": {}})
        return {"result": result}
    except:
        return {"error": "Invalid expression"}, 400

# ===================== HASH SECURISÉ =====================
@app.route("/hash", methods=["POST"])
def hash_password():
    pwd = request.json.get("password")
    hashed = hashlib.sha256(pwd.encode()).hexdigest()
    return {"sha256": hashed}

# ===================== LECTURE FICHIER SECURISÉE =====================
@app.route("/readfile", methods=["POST"])
def readfile():
    filename = request.json.get("filename")

    BASE_DIR = "./files"
    filepath = os.path.abspath(os.path.join(BASE_DIR, filename))

    # ✅ Anti LFI
    if not filepath.startswith(os.path.abspath(BASE_DIR)):
        return {"error": "Access denied"}, 403

    try:
        with open(filepath, "r") as f:
            return {"content": f.read()}
    except:
        return {"error": "File not found"}, 404

# ===================== DEBUG DESACTIVÉ =====================
@app.route("/debug", methods=["GET"])
def debug():
    return {"error": "Debug disabled in production"}, 403

@app.route("/hello", methods=["GET"])
def hello():
    return {"message": "Secure DevSecOps API"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
