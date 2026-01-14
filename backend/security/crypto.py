import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from settings import settings


class EncryptionError(Exception):
    pass


def _load_key() -> bytes:
    raw = settings.encryption_key
    if not raw:
        raise EncryptionError("ENCRYPTION_KEY is required")
    try:
        if all(c in "0123456789abcdef" for c in raw.lower()) and len(raw) in (32, 64):
            key = bytes.fromhex(raw)
        else:
            key = base64.b64decode(raw)
    except Exception as exc:
        raise EncryptionError("Invalid ENCRYPTION_KEY format") from exc
    if len(key) not in (16, 24, 32):
        raise EncryptionError("ENCRYPTION_KEY must be 16, 24, or 32 bytes")
    return key


def encrypt_text(plaintext: str) -> str:
    key = _load_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_text(token: str) -> str:
    key = _load_key()
    raw = base64.b64decode(token)
    nonce = raw[:12]
    ciphertext = raw[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
