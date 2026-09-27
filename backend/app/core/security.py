"""Hash de senha e tokens de sessão assinados.

Implementado só com a biblioteca padrão (hashlib/hmac/secrets) para não
adicionar novas dependências ao projeto (nada de passlib/bcrypt/PyJWT).
PBKDF2-HMAC-SHA256 é uma escolha aceita e amplamente usada para hash de
senha quando não se quer depender de uma lib externa como bcrypt/argon2.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time

from app.core.config import get_settings

_PBKDF2_ITERATIONS = 260_000
_TOKEN_TTL_SECONDS = 60 * 60 * 12  # 12 horas


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), _PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    try:
        algorithm, iterations_str, salt, expected_hex = hashed.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_str)
    except (ValueError, AttributeError):
        return False

    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), iterations)
    return hmac.compare_digest(digest.hex(), expected_hex)


def _signing_key() -> bytes:
    return get_settings().secret_key.encode("utf-8")


def create_session_token(subject: str) -> str:
    """Cria um token assinado (HMAC) contendo o id do usuário e a validade."""

    expires_at = int(time.time()) + _TOKEN_TTL_SECONDS
    payload = f"{subject}:{expires_at}"
    signature = hmac.new(_signing_key(), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    raw = f"{payload}:{signature}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")


def verify_session_token(token: str) -> str | None:
    """Valida um token e retorna o id do usuário (subject), ou None se inválido/expirado."""

    try:
        raw = base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
        subject, expires_at_str, signature = raw.split(":")
        expires_at = int(expires_at_str)
    except (ValueError, UnicodeDecodeError):
        return None

    payload = f"{subject}:{expires_at}"
    expected_signature = hmac.new(_signing_key(), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        return None
    if time.time() > expires_at:
        return None
    return subject
