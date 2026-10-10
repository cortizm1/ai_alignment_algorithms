"""jhu.nymo.finance — AI-usage transparency site for 601.433 (FastHTML + MonsterUI, no JavaScript).

Routes:
- GET  /               title card + homework table
- GET  /policy         public policy statement
- GET  /hw/{n}         one homework: commitment, sealed-at, opening form
- POST /hw/{n}/open    HTMX partial: verify + render report (opening never stored)
Every handler is wrapped; failures render an error card, never a traceback.

Run: uv run uvicorn web.app:app --host 127.0.0.1 --port 8010
"""

from __future__ import annotations

from typing import Any

from fasthtml.common import FastHTML, Title

from web import config, records, ui_components, verify


def create_app() -> Any:
    app = FastHTML(hdrs=ui_components.headers(), live=False, secret_key=config.SECRET_KEY)

    @app.route("/", methods=["get"])
    def home() -> Any:
        try:
            return Title("AI-usage transparency · 601.433"), ui_components.home_page(records.list_records())
        except Exception as exc:  # noqa: BLE001
            return ui_components.page(ui_components.error_card(str(exc)))

    @app.route("/policy", methods=["get"])
    def policy() -> Any:
        try:
            return Title("Policy · 601.433"), ui_components.policy_page(records.policy_markdown())
        except Exception as exc:  # noqa: BLE001
            return ui_components.page(ui_components.error_card(str(exc)))

    @app.route("/hw/{n}", methods=["get"])
    def homework(n: int) -> Any:
        try:
            rec = records.get_record(n)
            if rec is None:
                return Title("Not found"), ui_components.page(ui_components.error_card(f"No reel for homework {n}."))
            return Title(f"Reel {n} · 601.433"), ui_components.hw_page(rec)
        except Exception as exc:  # noqa: BLE001
            return ui_components.page(ui_components.error_card(str(exc)))

    @app.route("/hw/{n}/open", methods=["post"])
    def open_reel(n: int, opening: str = "") -> Any:
        try:
            rec = records.get_record(n)
            if rec is None or not rec.get("sealed"):
                return ui_components.verdict_partial(verify.Opened(False, "Nothing sealed for this homework yet."))
            return ui_components.verdict_partial(verify.open_record(rec, opening))
        except Exception as exc:  # noqa: BLE001
            return ui_components.error_card(str(exc))

    return app


app = create_app()
