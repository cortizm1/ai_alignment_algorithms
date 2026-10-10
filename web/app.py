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

from fasthtml.common import FastHTML, Response, Title, cookie

from web import config, records, ui_components, verify


def create_app() -> Any:
    app = FastHTML(hdrs=ui_components.headers(), live=False, secret_key=config.SECRET_KEY)

    @app.route("/", methods=["get"])
    def home(request, tour: int = 0) -> Any:
        """Landing page. The four-step tour pops up on the first visit (cookie) or on ?tour=1."""
        try:
            first_visit = request.cookies.get("tour_seen") != "1"
            body = Title("AI-usage transparency · 601.433"), ui_components.home_page(records.list_records(), show_tour=first_visit or bool(tour))
            return (*body, cookie("tour_seen", "1", max_age=60 * 60 * 24 * 365, samesite="lax")) if first_visit else body
        except Exception as exc:  # noqa: BLE001
            return ui_components.page(ui_components.error_card(str(exc)))

    @app.route("/policy", methods=["get"])
    def policy() -> Any:
        try:
            return Title("Policy · 601.433"), ui_components.policy_page(records.policy_markdown())
        except Exception as exc:  # noqa: BLE001
            return ui_components.page(ui_components.error_card(str(exc)))

    @app.route("/manifesto", methods=["get"])
    def manifesto() -> Any:
        """Public one-pager, readable by anyone: inline PDF, download, SHA3-256 as a subscript."""
        try:
            pdf = records.manifesto_pdf()
            if pdf is None:
                return Title("Manifesto"), ui_components.page(ui_components.error_card("The manifesto is not published yet."))
            return Title("Manifesto · 601.433"), ui_components.manifesto_page(pdf, records.get_record(0))
        except Exception as exc:  # noqa: BLE001
            return ui_components.page(ui_components.error_card(str(exc)))

    @app.route("/manifesto.pdf", methods=["get"])
    def manifesto_file() -> Any:
        """The same PDF as a file (inline for the viewer, downloadable by the browser)."""
        pdf = records.manifesto_pdf()
        if pdf is None:
            return Response("not published", status_code=404, media_type="text/plain")
        return Response(pdf, media_type="application/pdf", headers={"Content-Disposition": 'inline; filename="manifesto_onepager.pdf"'})

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
            return ui_components.verdict_partial(verify.open_record(rec, opening), n, opening)
        except Exception as exc:  # noqa: BLE001
            return ui_components.error_card(str(exc))

    @app.route("/hw/{n}/attachment/{i}", methods=["post"])
    def download_attachment(n: int, i: int, opening: str = "") -> Any:
        """Decrypt one attachment and hand it to the browser as a file. Stateless: the opening rides in the POST."""
        try:
            rec = records.get_record(n)
            att = verify.open_attachment(rec, opening, i) if rec else None
            if att is None:
                return Response("does not open", status_code=403, media_type="text/plain")
            return Response(att.data, media_type=att.mime,
                            headers={"Content-Disposition": f'attachment; filename="{att.name}"', "Cache-Control": "no-store"})
        except Exception as exc:  # noqa: BLE001
            return Response(str(exc), status_code=500, media_type="text/plain")

    return app


app = create_app()
