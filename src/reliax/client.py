"""The thin client: one call out, one certificate back.

    import reliax
    reliax.configure("https://reliax.internal.example", api_key="...")
    out = reliax.assess({"income": 54000, "dti": 0.31}, reliax.Context(score=0.04, model_reason_codes=["R01", "R07"]))
    out.route            # "ALLOW", "REVIEW" or "BLOCK"
    out.certificate      # the signed payload, as the platform recorded it
    out.certificate_text # the stored wording, verbatim

The context carries the model's score and its reason codes; both are recorded
as received and never altered. The platform runs inside the customer's
infrastructure; decision data never leaves it. Standard library only.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict


@dataclass
class Context:
    """What the decision engine knows at the moment of the call."""
    score: float                                   # the model's output: probability, logit or scorecard points
    model_reason_codes: list = field(default_factory=list)   # recorded as received
    segment: str | None = None                     # a business segment named in the policy, never a protected attribute
    model_id: str | None = None
    prediction_id: str | None = None
    label: int | None = None                       # the model's answer, if the engine has already taken it
    extra: dict = field(default_factory=dict)      # anything else the policy reads; stored as received

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class Assessment:
    route: str
    certificate: dict
    audit_id: str | None
    raw: dict

    @property
    def certificate_text(self) -> str:
        return self.certificate.get("certificate_text", "")

    @property
    def reason_codes(self) -> list:
        return list(self.certificate.get("routing", {}).get("reason_codes", []))


class ReliaxError(RuntimeError):
    pass


class Client:
    def __init__(self, base_url: str, api_key: str | None = None, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _post(self, path: str, body: dict) -> dict:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(self.base_url + path, data=data, method="POST",
                                     headers={"Content-Type": "application/json", "Accept": "application/json",
                                              "User-Agent": "reliax-sdk"})
        if self.api_key:
            req.add_header("Authorization", f"Bearer {self.api_key}")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise ReliaxError(f"{e.code} from {path}: {e.read().decode('utf-8', 'replace')[:300]}") from None
        except urllib.error.URLError as e:
            raise ReliaxError(f"cannot reach {self.base_url}: {e.reason}") from None

    def assess(self, query, ctx: Context) -> Assessment:
        """Certify one decision. query is the model input (or its fingerprint); ctx carries the model's output."""
        out = self._post("/v1/assess", {"input": query, "context": ctx.as_dict()})
        cert = out.get("certificate") or out
        route = out.get("route") or out.get("routing") or cert.get("routing", {}).get("route")
        if route not in ("ALLOW", "REVIEW", "BLOCK"):
            raise ReliaxError(f"no route in the response: {list(out)[:8]}")
        return Assessment(route=route, certificate=cert, audit_id=out.get("audit_id") or cert.get("audit_id"), raw=out)

    def health(self) -> dict:
        req = urllib.request.Request(self.base_url + "/v1/health", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))


_default: Client | None = None


def configure(base_url: str, api_key: str | None = None, timeout: float = 5.0) -> Client:
    """Set the client that reliax.assess uses."""
    global _default
    _default = Client(base_url, api_key=api_key, timeout=timeout)
    return _default


def assess(query, ctx: Context) -> Assessment:
    if _default is None:
        raise ReliaxError("call reliax.configure(base_url, api_key) first")
    return _default.assess(query, ctx)


def verify(path: str, recompute: bool = False) -> dict:
    """Verify a record file with reliax-certificate, if it is installed."""
    try:
        from reliax_certificate.verify import verify_file
    except ImportError:
        raise ReliaxError("pip install reliax-certificate to verify records") from None
    return verify_file(path, recompute=recompute)
