"""Open a sealed record with an opening token. Pure function; never stores the opening."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from transparency import crypto


@dataclass(frozen=True)
class Opened:
    ok: bool
    message: str
    report: str = ""
    transcript: str = ""


def open_record(rec: dict[str, Any], token: str) -> Opened:
    """Decrypt report (and transcript if present) and check the Pedersen commitment."""
    try:
        opening = crypto.decode_opening(token)
    except ValueError as exc:
        return Opened(False, f"Malformed opening: {exc}")
    try:
        sealed = crypto.decode_sealed(rec["sealed"])
        report = crypto.open_sealed(sealed, opening).decode()
    except (KeyError, ValueError) as exc:
        return Opened(False, f"Does not open: {exc}")
    transcript = ""
    if rec.get("transcript"):
        try:
            transcript = crypto.open_attachment(rec["transcript"], sealed.commitment, opening).decode()
        except ValueError as exc:
            transcript = f"_Transcript attachment failed to open: {exc}_"
    return Opened(True, "Commitment verified: the report opens the published commitment.", report, transcript)
