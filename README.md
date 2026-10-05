# reliax-sdk

**One call out, one certificate back.** The thin Python client for the Reliax
platform. Apache-2.0. Standard library only. Terms used here are defined in
the [glossary](https://github.com/reliax-io#terms).

The client talks to a running Reliax platform, which holds the calibration
cohorts, the drift state and the record store. Installing the client alone
does nothing until it is pointed at one; how to get a platform is on the
[organisation page](https://github.com/reliax-io#with-the-platform). To try
the method without a platform, use
[reliax-core](https://github.com/reliax-io/reliax-core) directly.

```
pip install reliax-sdk
```

PyPI package `reliax-sdk`, import name `reliax`.

```python
import reliax

reliax.configure("https://reliax.internal.example", api_key="...")   # your platform instance
out = reliax.assess(
    {"income": 54000, "dti": 0.31},                                     # the model input, or its fingerprint
    reliax.Context(score=0.04, model_reason_codes=["R01", "R07"], segment="thin-file"),  # score: your model's output
)
print(out.route, out.reason_codes)   # ALLOW ['CERTIFIED']
print(out.certificate_text)          # the wording stored on the record, verbatim
print(out.audit_id)
```

The context carries the model's score and its own reason codes. Both are
recorded as received and never altered; adverse-action reasons come from the
model's codes, never from Reliax.

## What comes back

A certificate (envelope schema v16, [reliax-certificate](https://github.com/reliax-io/reliax-certificate))
and a route. The certificate says four things: three guarantees and one exact
output. A guarantee holds on exchangeable data at the stated level with no
assumption on the model; an exact output is recomputed bit for bit from the
record, so a verifier can replay it.

| | Class |
|---|---|
| Whether this answer can be relied on: a prediction set that contains the true outcome at least 1−α of the time, marginally and per declared segment, from a cohort named with its size, freeze date and hash | guarantee |
| Whether the guarantee covers this input: the credibility p-value | guarantee |
| Whether the population has moved: the drift state on this segment's stream, and the dated outcome recheck | guarantee |
| The route, the row that matched, the route trace and the reasons | exact |

The routing rule looks only at what the certificate guarantees, and the
thresholds it applies come from a policy that you write and keep under version
control. The criticality score orders the review queue and never enters a
rule. How the certificate may and may not be read is set out once, in
[Read this correctly](https://github.com/reliax-io#read-this-correctly).

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
| [reliax-core](https://github.com/reliax-io/reliax-core) | The method: conformal sets, the calibrated bracket, the drift test, the credibility p-value, the routing rule | Apache-2.0 |
| [reliax-certificate](https://github.com/reliax-io/reliax-certificate) | The certificate schema, the hash chain, the wording template, the fidelity check and the verifier | Apache-2.0 |
| reliax-sdk (this package) | The client | Apache-2.0 |
| Reliax platform | Calibration builder, reliability engine, review queues, audit service, dashboard; runs inside your infrastructure | Source-available |

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
