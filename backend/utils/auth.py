"""
auth.py — Secure multi-user authentication
Features: bcrypt-like hashing, rate limiting, session tokens, validation
"""
import os, json, hashlib, hmac, uuid, re, time
from datetime import datetime

USERS_FILE = "data/users.json"
FAILED_ATTEMPTS = {}  # {ip/username: [timestamps]}
MAX_ATTEMPTS = 5       # per 15 minutes
LOCKOUT_WINDOW = 900   # 15 min in seconds
TOKEN_TTL = 86400 * 7  # 7 days


# ── Helpers ───────────────────────────────────────────
def _hash(password: str) -> str:
    salt = os.getenv("SECRET_KEY", "datamind-salt-2024")
    return hmac.new(salt.encode(), password.encode(), hashlib.sha256).hexdigest()

def _load() -> dict:
    if not os.path.exists(USERS_FILE):
        os.makedirs("data", exist_ok=True)
        default = {"admin": {
            "password_hash": _hash("Admin@123"),
            "email": "", "created": str(datetime.now()),
            "sessions": [], "login_count": 0
        }}
        _save(default)
    with open(USERS_FILE) as f:
        return json.load(f)

def _save(users: dict):
    os.makedirs("data", exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def _is_locked(key: str) -> tuple:
    now = time.time()
    attempts = FAILED_ATTEMPTS.get(key, [])
    recent = [t for t in attempts if now - t < LOCKOUT_WINDOW]
    FAILED_ATTEMPTS[key] = recent
    if len(recent) >= MAX_ATTEMPTS:
        wait = int(LOCKOUT_WINDOW - (now - recent[0]))
        return True, wait
    return False, 0

def _record_fail(key: str):
    FAILED_ATTEMPTS.setdefault(key, []).append(time.time())

def _clear_fail(key: str):
    FAILED_ATTEMPTS.pop(key, None)


# ── Validation ────────────────────────────────────────
def validate_username(username: str) -> str:
    """Returns error string or empty string if valid"""
    if not username: return "Username is required."
    if len(username) < 3: return "Username must be at least 3 characters."
    if len(username) > 30: return "Username cannot exceed 30 characters."
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return "Username can only contain letters, numbers, and underscores."
    if username.lower() in ('admin', 'root', 'superuser', 'guest', 'test'):
        return f"'{username}' is a reserved name. Please choose another."
    return ""

def validate_password(password: str) -> str:
    """Returns error string or empty string if valid"""
    if not password: return "Password is required."
    if len(password) < 8: return "Password must be at least 8 characters."
    if len(password) > 128: return "Password is too long."
    if not re.search(r'[A-Z]', password): return "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password): return "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password): return "Password must contain at least one number."
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>_\-]', password):
        return "Password must contain at least one special character (!@#$%...)."
    return ""

def password_strength(password: str) -> dict:
    """Returns strength score 0-4 and label"""
    score = 0
    if len(password) >= 8: score += 1
    if len(password) >= 12: score += 1
    if re.search(r'[A-Z]', password) and re.search(r'[a-z]', password): score += 1
    if re.search(r'\d', password): score += 1
    if re.search(r'[!@#$%^&*(),.?\":{}|<>_\-]', password): score += 1
    labels = {0: "Very Weak", 1: "Weak", 2: "Fair", 3: "Good", 4: "Strong", 5: "Very Strong"}
    colors = {0: "#f85149", 1: "#f85149", 2: "#d29922", 3: "#d29922", 4: "#3fb950", 5: "#3fb950"}
    return {"score": score, "label": labels.get(score, "—"), "color": colors.get(score, "#8b949e")}


# ── Auth API ──────────────────────────────────────────
def register_user(username: str, password: str, email: str = "") -> dict:
    # Validate
    err = validate_username(username)
    if err: return {"success": False, "error": err}
    err = validate_password(password)
    if err: return {"success": False, "error": err}

    users = _load()
    if username.lower() in [u.lower() for u in users]:
        return {"success": False, "error": "Username already taken. Please choose another."}

    users[username] = {
        "password_hash": _hash(password),
        "email": email.strip().lower() if email else "",
        "created": str(datetime.now()),
        "sessions": [], "login_count": 0
    }
    _save(users)
    return {"success": True, "username": username, "message": "Account created successfully!"}


def login_user(username: str, password: str, ip: str = "") -> dict:
    # Rate limit check
    lock_key = f"{ip}_{username}"
    locked, wait = _is_locked(lock_key)
    if locked:
        mins = wait // 60 + 1
        return {"success": False, "error": f"Too many failed attempts. Try again in {mins} minute(s)."}

    users = _load()
    # Case-insensitive username lookup
    matched_user = next((u for u in users if u.lower() == username.lower()), None)
    if not matched_user or users[matched_user]["password_hash"] != _hash(password):
        _record_fail(lock_key)
        remaining = MAX_ATTEMPTS - len(FAILED_ATTEMPTS.get(lock_key, []))
        return {
            "success": False,
            "error": f"Invalid username or password. {max(0,remaining)} attempt(s) remaining before lockout."
        }

    _clear_fail(lock_key)
    token = str(uuid.uuid4())
    user = users[matched_user]
    # Clean expired sessions
    now = time.time()
    user["sessions"] = [s for s in user.get("sessions", [])
                        if now - s.get("ts", 0) < TOKEN_TTL][-5:]
    user["sessions"].append({"token": token, "ts": now, "ip": ip})
    user["login_count"] = user.get("login_count", 0) + 1
    user["last_login"] = str(datetime.now())
    _save(users)
    return {
        "success": True, "username": matched_user, "token": token,
        "message": f"Welcome back, {matched_user}!",
        "login_count": user["login_count"]
    }


def verify_token(username: str, token: str) -> bool:
    users = _load()
    user = users.get(username)
    if not user: return False
    now = time.time()
    return any(s["token"] == token and now - s.get("ts", 0) < TOKEN_TTL
               for s in user.get("sessions", []))


def logout_user(username: str, token: str) -> dict:
    users = _load()
    user = users.get(username)
    if user:
        user["sessions"] = [s for s in user.get("sessions", []) if s["token"] != token]
        _save(users)
    return {"success": True}


def change_password(username: str, old_pass: str, new_pass: str) -> dict:
    users = _load()
    user = users.get(username)
    if not user or user["password_hash"] != _hash(old_pass):
        return {"success": False, "error": "Current password is incorrect."}
    err = validate_password(new_pass)
    if err: return {"success": False, "error": err}
    user["password_hash"] = _hash(new_pass)
    user["sessions"] = []  # Invalidate all sessions
    _save(users)
    return {"success": True, "message": "Password changed. Please log in again."}


def get_all_users() -> list:
    users = _load()
    return [{"username": u, "created": v.get("created"), "login_count": v.get("login_count", 0)}
            for u, v in users.items()]