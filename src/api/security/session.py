import hashlib
import secrets


def generate_session() -> str:
    return secrets.token_urlsafe(32)

def hash_session(session_token: str) -> str:
    return hashlib.sha256(session_token.encode()).hexdigest()
