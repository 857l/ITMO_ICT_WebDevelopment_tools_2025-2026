import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Optional

from core.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES


# ---------- Хэширование паролей (PBKDF2-HMAC-SHA256, вручную, без passlib) ----------

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), 100_000
    ).hex()
    # храним соль и хэш вместе через разделитель
    return f"{salt}${hashed}"


def verify_password(password: str, stored: str) -> bool:
    salt, hashed = stored.split("$")
    check = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), 100_000
    ).hex()
    return hmac.compare_digest(check, hashed)


# ---------- JWT (вручную, без python-jose/pyjwt) ----------

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(user_id: int) -> str:
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "exp": int(time.time()) + JWT_EXPIRE_MINUTES * 60,
        "iat": int(time.time()),
    }
    header_b64 = _b64url_encode(json.dumps(header).encode())
    payload_b64 = _b64url_encode(json.dumps(payload).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    signature_b64 = _b64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_access_token(token: str) -> Optional[dict]:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError:
        return None

    signing_input = f"{header_b64}.{payload_b64}".encode()
    expected_signature = hmac.new(
        JWT_SECRET.encode(), signing_input, hashlib.sha256
    ).digest()
    expected_signature_b64 = _b64url_encode(expected_signature)

    if not hmac.compare_digest(expected_signature_b64, signature_b64):
        return None  # подпись не совпадает — токен подделан или неверный секрет

    payload = json.loads(_b64url_decode(payload_b64))

    if payload.get("exp", 0) < time.time():
        return None  # токен просрочен

    return payload
