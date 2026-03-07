"""
backend/routes/auth_routes.py
Login, Register, Logout endpoints
"""
from flask import Blueprint, request, jsonify, session
from backend.utils.auth import register_user, login_user, logout_user, verify_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    body = request.get_json() or {}
    result = register_user(body.get("username",""), body.get("password",""))
    if result["success"]:
        session["username"] = result["username"]
    return jsonify(result)

@auth_bp.route("/login", methods=["POST"])
def login():
    body = request.get_json() or {}
    result = login_user(body.get("username",""), body.get("password",""))
    if result["success"]:
        session["username"] = result["username"]
        session["token"] = result["token"]
    return jsonify(result)

@auth_bp.route("/logout", methods=["POST"])
def logout():
    username = session.get("username","")
    token = session.get("token","")
    logout_user(username, token)
    session.clear()
    return jsonify({"success": True})

@auth_bp.route("/me", methods=["GET"])
def me():
    username = session.get("username")
    token = session.get("token")
    if not username or not token or not verify_token(username, token):
        return jsonify({"logged_in": False})
    return jsonify({"logged_in": True, "username": username})
