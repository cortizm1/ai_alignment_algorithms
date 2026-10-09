"""Shared crypto for the transparency site.
Scheme per homework N:
  key   = 20-char base32 random passphrase (100 bits), printed in the LaTeX header of the submission.
  K     = PBKDF2-HMAC-SHA256(key, salt, 200k iters) -> AES-256-GCM key (Web Crypto can do the same in-browser).
  blob  = salt || nonce || AESGCM(K, nonce, report_markdown)
  commitment = SHA-256(report_markdown), printed in the LaTeX header and on the public page.
Anyone can verify: decrypt with the key from the submission, hash the plaintext, compare with the
commitment published before the deadline. The ciphertext is public; the key is only in the PDF the graders hold."""
import base64, hashlib, json, os, secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
ITER = 200_000
def new_key() -> str:
    raw = base64.b32encode(secrets.token_bytes(13)).decode().rstrip("=")[:20]
    return "-".join(raw[i:i+5] for i in range(0, 20, 5))      # e.g. Q7MZX-K2PLA-9DF3R-TBW8C
def derive(key: str, salt: bytes) -> bytes:
    return PBKDF2HMAC(hashes.SHA256(), 32, salt, ITER).derive(key.replace("-", "").upper().encode())
def encrypt(key: str, plaintext: str) -> dict:
    salt, nonce = os.urandom(16), os.urandom(12)
    ct = AESGCM(derive(key, salt)).encrypt(nonce, plaintext.encode(), None)
    return {"salt": base64.b64encode(salt).decode(), "nonce": base64.b64encode(nonce).decode(),
            "ct": base64.b64encode(ct).decode(), "kdf": f"PBKDF2-SHA256/{ITER}", "cipher": "AES-256-GCM"}
def decrypt(key: str, blob: dict) -> str:
    return AESGCM(derive(key, base64.b64decode(blob["salt"]))).decrypt(
        base64.b64decode(blob["nonce"]), base64.b64decode(blob["ct"]), None).decode()
def commitment(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode()).hexdigest()
