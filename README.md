# reliax-sdk

**One call out, one certificate back.** The thin Python client for the Reliax
platform. Apache-2.0. Standard library only.

```
pip install reliax-sdk
```

```python
import reliax

reliax.configure("https://reliax.internal.example", api_key="...")
out = reliax.assess(
    {"income": 54000, "dti": 0.31},                       # the model input, or its fingerprint
    reliax.Context(score=0.04, model_reason_codes=["R01", "R07"], segment="thin-file"),
)
out.route             # "ALLOW", "REVIEW" or "BLOCK"
out.reason_codes      # e.g. ["CERTIFIED"] or ["SET_AMBIGUOUS"]
out.certificate_text  # the wording stored in the record, verbatim
out.audit_id
```

The context carries the model's score and its own reason codes. Both are
recorded as received and never altered; adverse-action reasons come from the
model's codes, never from Reliax.

## What comes back

A certificate (envelope schema v16, [reliax-certificate](https://github.com/reliax-io/reliax-certificate))
and a route. The certificate says four things:

| | Class |
|---|---|
| Whether this answer can be relied on: a prediction set that contains the true outcome at least 1−α of the time, marginally and per declared segment, from a cohort named with its size, freeze date and hash | guarantee |
| Whether the guarantee covers this input: the credibility p-value | guarantee |
| Whether the population has moved: the drift state on this segment's stream, and the dated outcome recheck | guarantee |
| The route, the row that matched, the route trace and the reasons | exact |

Routing reads certified quantities only, in a fixed order, under a policy you
write and version. The criticality score orders the review queue and never
enters a rule. Nothing here is a probability that a given decision is right,
and the certificate never prints a percentage next to a decision.

## Verify a record without us

```
pip install reliax-certificate
reliax verify record.json            # schema, hash chain, wording, routing
reliax verify record.json --recompute   # plus the route re-run with reliax-core
```

`reliax.verify(path)` does the same from Python when reliax-certificate is
installed.

## Where the pieces live

| Package | What it is | Licence |
|---|---|---|
| [reliax-core](https://github.com/reliax-io/reliax-core) | The method: conformal sets, Venn-Abers brackets, the test martingale, the credibility p-value, the fast-loop evaluator with its route trace and reasons | Apache-2.0 |
| [reliax-certificate](https://github.com/reliax-io/reliax-certificate) | The certificate schema, the hash chain, the wording template, the fidelity check and the verifier | Apache-2.0 |
| reliax-sdk (this package) | The client | Apache-2.0 |
| Reliax platform | Calibration builder, reliability engine, review queues, audit service, dashboard; runs inside your infrastructure | Source-available, licensed |

Everything that routes a decision or is written on the certificate is open.
The platform holds the state and the workflow.

## Evidence

Measured on public credit data and reproducible end to end at
[reliax-evaluation](https://github.com/reliax-io/reliax-evaluation), negative
results included; the whitepaper is at [reliax.io/whitepaper.html](https://reliax.io/whitepaper.html).

## Licence

Apache-2.0. See [LICENSE](LICENSE).

## About this documentation

The documentation in this repository was written with the help of AI and
reviewed by the Reliax team.
