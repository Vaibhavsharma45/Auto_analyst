"""
backend/utils/auth.py
Simple multi-user system — username/password with per-user session isolation
No database needed — users stored in users.json
"""
import os
import json
import hashlib
import uuid
from datetime import datetime

USERS_FILE = "data/users.json"


def _load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        os.makedirs("data", exist_ok=True)
        # Default admin user
        _save_users({"admin": {"password_hash": _hash("admin123"),
                                "created": str(datetime.now()), "sessions": []}})
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def _save_users(users: dict):
    os.makedirs("data", exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username: str, password: str) -> dict:
    if len(username) < 3:
        return {"success": False, "error": "Username must be 3+ characters"}
    if len(password) < 6:
        return {"success": False, "error": "Password must be 6+ characters"}
    users = _load_users()
    if username in users:
        return {"success": False, "error": "Username already exists"}
    users[username] = {"password_hash": _hash(password),
                       "created": str(datetime.now()), "sessions": []}
    _save_users(users)
    return {"success": True, "username": username}


def login_user(username: str, password: str) -> dict:
    users = _load_users()
    user = users.get(username)
    if not user or user["password_hash"] != _hash(password):
        return {"success": False, "error": "Invalid username or password"}
    token = str(uuid.uuid4())
    user["sessions"].append({"token": token, "created": str(datetime.now())})
    user["sessions"] = user["sessions"][-5:]  # Keep last 5 sessions
    _save_users(users)
    return {"success": True, "username": username, "token": token}


def verify_token(username: str, token: str) -> bool:
    users = _load_users()
    user = users.get(username)
    if not user:
        return False
    return any(s["token"] == token for s in user.get("sessions", []))


def logout_user(username: str, token: str) -> dict:
    users = _load_users()
    user = users.get(username)
    if user:
        user["sessions"] = [s for s in user.get("sessions", []) if s["token"] != token]
        _save_users(users)
    return {"success": True}


def get_all_users() -> list:
    users = _load_users()
    return [{"username": u, "created": v.get("created")} for u, v in users.items()]
