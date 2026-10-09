"""Commitment-and-reveal scheme for the AI-usage transparency reports.

Pure functions, no I/O. Stack-independent: the same module runs in the
sealing tool (harness side) and in the verifier page (FastHTML side).

Primitives (all via libsodium through pysodium, plus hashlib for SHA-3):

    hash        SHA3-256 (Keccak sponge)                        hashlib
    commitment  Pedersen over ristretto255: C = m*G + r*H       pysodium
    encryption  ChaCha20-Poly1305 (IETF, 96-bit nonce), AEAD    pysodium

Per report R (bytes):
    m  = SHA3-256(R) reduced mod the group order (ristretto scalar)
    r  = random blinding scalar
    C  = m*G + r*H                              <- published BEFORE the deadline
    k  = random 256-bit key; ct = ChaCha20Poly1305(k, nonce, R, ad=C)
                                                <- ct, nonce published with C
    opening = (k, r)                            <- printed in the submitted PDF

Verify: decrypt ct with k (AEAD binds it to C via associated data), recompute
m from the plaintext, check C == m*G + r*H.

Why Pedersen and not SHA3(R): the report is short and structured, so a bare hash
commitment is not hiding (guess-and-check). Pedersen is perfectly hiding and
binding under the discrete-log assumption in ristretto255 (prime order, no
cofactor issues). H = from_hash(SHA3-512(DOMAIN)) so nobody knows log_G(H).
"""

from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass

import pysodium as sodium

DOMAIN_H = b"nymo.finance/601.433-transparency/H/v1"
NONCE_BYTES = 12  # ChaCha20-Poly1305 IETF
KEY_BYTES = 32
SCALAR_BYTES = sodium.crypto_core_ristretto255_SCALARBYTES
POINT_BYTES = sodium.crypto_core_ristretto255_BYTES


@dataclass(frozen=True)
class Sealed:
    """Everything that is PUBLISHED for one report."""

    commitment: bytes  # 32-byte ristretto255 point C
    nonce: bytes  # 12 bytes
    ciphertext: bytes  # ChaCha20-Poly1305 output (includes 16-byte tag)


@dataclass(frozen=True)
class Opening:
    """Everything that goes in the submitted PDF header (never published)."""

    key: bytes  # 32 bytes
    blinding: bytes  # 32-byte scalar r


def generator_h() -> bytes:
    """Second Pedersen generator H, derived from a fixed domain string via hash-to-group."""
    return sodium.crypto_core_ristretto255_from_hash(hashlib.sha3_512(DOMAIN_H).digest())


def message_scalar(report: bytes) -> bytes:
    """Map a report to a scalar: SHA3-256 (as 64-byte zero-padded input) reduced mod the group order."""
    digest = hashlib.sha3_256(report).digest()
    return sodium.crypto_core_ristretto255_scalar_reduce(digest + bytes(32))


def commit(report: bytes, blinding: bytes) -> bytes:
    """Pedersen commitment C = m*G + r*H for m = message_scalar(report)."""
    m_g = sodium.crypto_scalarmult_ristretto255_base(message_scalar(report))
    r_h = sodium.crypto_scalarmult_ristretto255(blinding, generator_h())
    return sodium.crypto_core_ristretto255_add(m_g, r_h)


def seal(report: bytes) -> tuple[Sealed, Opening]:
    """Commit to and encrypt a report. Returns (public part, secret opening)."""
    blinding = sodium.crypto_core_ristretto255_scalar_random()
    key = os.urandom(KEY_BYTES)
    nonce = os.urandom(NONCE_BYTES)
    commitment = commit(report, blinding)
    ciphertext = sodium.crypto_aead_chacha20poly1305_ietf_encrypt(report, commitment, nonce, key)
    return Sealed(commitment, nonce, ciphertext), Opening(key, blinding)


def open_sealed(sealed: Sealed, opening: Opening) -> bytes:
    """Decrypt and verify. Returns the report, or raises ValueError on any failure."""
    try:
        report = sodium.crypto_aead_chacha20poly1305_ietf_decrypt(
            sealed.ciphertext, sealed.commitment, sealed.nonce, opening.key
        )
    except Exception as exc:  # pysodium raises a bare ValueError on auth failure
        raise ValueError("decryption failed: wrong key or tampered ciphertext") from exc
    if not hmac.compare_digest(commit(report, opening.blinding), sealed.commitment):
        raise ValueError("commitment mismatch: report does not open the published commitment")
    return report


# ---- text encodings for the PDF header and the site --------------------------


def encode_opening(opening: Opening) -> str:
    """`<key-hex>.<blinding-hex>` — one copy-pasteable token for the PDF header."""
    return f"{opening.key.hex()}.{opening.blinding.hex()}"


def decode_opening(token: str) -> Opening:
    """Inverse of encode_opening; tolerant of whitespace and case."""
    key_hex, _, blind_hex = token.strip().lower().partition(".")
    key, blinding = bytes.fromhex(key_hex), bytes.fromhex(blind_hex)
    if len(key) != KEY_BYTES or len(blinding) != SCALAR_BYTES:
        raise ValueError("opening token must be <64 hex>.<64 hex>")
    return Opening(key, blinding)


def encode_sealed(sealed: Sealed) -> dict[str, str]:
    """JSON-friendly public record."""
    return {
        "commitment": sealed.commitment.hex(),
        "nonce": sealed.nonce.hex(),
        "ciphertext": sealed.ciphertext.hex(),
        "scheme": "pedersen-ristretto255+sha3-256+chacha20poly1305-ietf/v1",
    }


def decode_sealed(record: dict[str, str]) -> Sealed:
    """Inverse of encode_sealed."""
    return Sealed(
        bytes.fromhex(record["commitment"]),
        bytes.fromhex(record["nonce"]),
        bytes.fromhex(record["ciphertext"]),
    )
