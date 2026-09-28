"""The client shapes requests and responses as documented; no network in tests."""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
import reliax  # noqa: E402


def test_context_is_recorded_as_given():
    ctx = reliax.Context(score=0.04, model_reason_codes=["R01"], segment="thin-file")
    d = ctx.as_dict()
    assert d["score"] == 0.04 and d["model_reason_codes"] == ["R01"] and d["segment"] == "thin-file"


def test_assess_parses_a_response(monkeypatch):
    client = reliax.Client("https://example.invalid", api_key="k")
    sent = {}

    def fake_post(path, body):
        sent["path"], sent["body"] = path, body
        return {"route": "ALLOW", "audit_id": "rxe_1", "certificate": {"audit_id": "rxe_1", "certificate_text": "text",
                                                                      "routing": {"route": "ALLOW", "reason_codes": ["CERTIFIED"]}}}
    monkeypatch.setattr(client, "_post", fake_post)
    out = client.assess({"a": 1}, reliax.Context(score=0.1))
    assert sent["path"] == "/v1/assess" and sent["body"]["context"]["score"] == 0.1
    assert (out.route, out.audit_id, out.certificate_text, out.reason_codes) == ("ALLOW", "rxe_1", "text", ["CERTIFIED"])


def test_assess_requires_configuration():
    reliax.client._default = None
    try:
        reliax.assess({}, reliax.Context(score=0.5))
    except reliax.ReliaxError as e:
        assert "configure" in str(e)
    else:
        raise AssertionError("expected ReliaxError")
