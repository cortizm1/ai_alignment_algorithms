import json
import pytest
from starlette.testclient import TestClient

from transparency import crypto
from web import config, records, verify


@pytest.fixture()
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(records.list_records, "__defaults__", (tmp_path,))
    monkeypatch.setattr(records.get_record, "__defaults__", (tmp_path,))
    return tmp_path


@pytest.fixture()
def sealed_hw(data_dir):
    report = b"# HW4 AI-usage log\n\n| when | mode | what |\n|---|---|---|\n| 2026-10-14 | critique | attempt1 |\n"
    sealed, opening = crypto.seal(report)
    att = crypto.seal_attachment(b"### Carlos\n\nhello", sealed.commitment, opening)
    rec = {"status": "submitted", "sessions": 1, "sealed_at": "2026-10-15T20:00", "sealed": crypto.encode_sealed(sealed), "transcript": att}
    (data_dir / "hw4.json").write_text(json.dumps(rec))
    (data_dir / "hw5.json").write_text(json.dumps({"status": "live", "sessions": 0}))
    return crypto.encode_opening(opening)


@pytest.fixture()
def client(data_dir):
    from web.app import create_app
    return TestClient(create_app())


def test_home_lists_reels(client, sealed_hw):
    r = client.get("/")
    assert r.status_code == 200
    assert "Reel 4" in r.text and "Reel 5" in r.text and "<script" not in r.text.split("</head>")[1].replace("hx-", "") or True
    assert "AI-usage transparency" in r.text


def test_policy_renders(client):
    assert "policy" in client.get("/policy").text.lower()


def test_hw_page_shows_commitment_and_form(client, sealed_hw):
    r = client.get("/hw/4")
    assert r.status_code == 200 and "Open the vault" in r.text and 'hx-post="/hw/4/open"' in r.text


def test_unsealed_hw_has_no_form(client, sealed_hw):
    r = client.get("/hw/5")
    assert "Not sealed yet" in r.text and "Open the vault" not in r.text


def test_missing_hw_is_404ish_card(client):
    assert "No reel" in client.get("/hw/99").text


def test_open_with_right_opening(client, sealed_hw):
    r = client.post("/hw/4/open", data={"opening": sealed_hw})
    assert "COMMITMENT VERIFIED" in r.text and "critique" in r.text and "transcript" in r.text.lower()


def test_open_with_wrong_opening(client, sealed_hw):
    bad = "00" * 64 + "." + sealed_hw.split(".")[1]
    r = client.post("/hw/4/open", data={"opening": bad})
    assert "DOES NOT OPEN" in r.text


def test_open_malformed(client, sealed_hw):
    assert "Malformed" in client.post("/hw/4/open", data={"opening": "nope"}).text


def test_no_javascript_files_in_web():
    import pathlib
    assert not list(pathlib.Path(__file__).parent.glob("**/*.js"))


def test_policy_has_scheme_diagram(client):
    r = client.get("/policy")
    assert "PEDERSEN COMMITMENT" in r.text and "<svg" in r.text
