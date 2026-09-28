"""Reliax SDK: one call out, one certificate back.

Reliax sits beside a model, never inside it, and attaches a certificate to
each decision before it is acted on. The certificate says whether this answer
can be relied on, at a guaranteed error rate; whether the guarantee covers this
input; whether the population has moved; and it is written to a hash-chained
record an auditor can replay. Routing (ALLOW, REVIEW, BLOCK) runs on the
certified quantities only, under a policy the deployer owns. BLOCK never means
decline: a person decides.

This package is the thin client. The method code is reliax-core, the
certificate format and the verifier are reliax-certificate, and the platform
that holds the state runs inside the customer's infrastructure.
"""
__version__ = "0.1.0"

from .client import Client, Context, Assessment, ReliaxError, configure, assess, verify

__all__ = ["__version__", "Client", "Context", "Assessment", "ReliaxError", "configure", "assess", "verify"]
