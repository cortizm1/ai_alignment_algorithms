"""Open a sealed record with an opening token. Pure functions; never store the opening."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from transparency import crypto
from web import records


@dataclass(frozen=True)
class Attachment:
    name: str
    mime: str
    data: bytes


@dataclass(frozen=True)
class Opened:
    ok: bool
    message: str
    report: str = ""
    attachments: list[Attachment] = field(default_factory=list)


def open_record(rec: dict[str, Any], token: str) -> Opened:
    """Decrypt the report, check the Pedersen commitment, then open every attachment."""
    try:
        opening = crypto.decode_opening(token)
    except ValueError as exc:
        return Opened(False, f"Malformed opening: {exc}")
    try:
        sealed = crypto.decode_sealed(rec["sealed"])
        report = crypto.open_sealed(sealed, opening).decode()
    except (KeyError, ValueError) as exc:
        return Opened(False, f"Does not open: {exc}")
    atts: list[Attachment] = []
    for a in records.attachments_of(rec):
        try:
            atts.append(Attachment(a["name"], a.get("mime", "application/octet-stream"),
                                   crypto.open_attachment(a, sealed.commitment, opening)))
        except ValueError:
            atts.append(Attachment(a["name"], "text/markdown", b"_attachment failed to open_"))
    return Opened(True, "Commitment verified: the report opens the published commitment.", report, atts)


def open_attachment(rec: dict[str, Any], token: str, index: int) -> Attachment | None:
    """One attachment by index, or None if the opening is wrong or the index is out of range."""
    opened = open_record(rec, token)
    if not opened.ok or index < 0 or index >= len(opened.attachments):
        return None
    return opened.attachments[index]
