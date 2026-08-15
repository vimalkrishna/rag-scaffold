# API Gateway + Lambda included in commit 1
# ADR 0002: Query Interface in Baseline (API Gateway + Lambda)

**Status:** Accepted

**Date:** 2026-08-09

**Commit:** [fill in — the commit that introduces QueryFunction/HttpApi]

## Context

Bedrock Knowledge Bases can be queried directly via the `bedrock-agent-runtime`
SDK (`Retrieve` / `RetrieveAndGenerate`) with no additional infrastructure —
console, CLI, or a boto3 script are all sufficient to prove the KB works.
The open question for this baseline commit was whether an HTTP-invocable
interface (Lambda behind API Gateway) belongs in the *first* commit, given
the scaffold's stated goal of "essential services only, no domain logic."
An HTTP endpoint is not strictly required to validate that ingestion →
embedding → retrieval → generation works end to end — it's required only
if something *external* needs to call the pipeline.

## Decision

Include a Lambda function (`QueryFunction`) fronted by an API Gateway
HTTP API in the baseline commit, exposing a single `POST /query` route
that invokes `bedrock-agent-runtime.retrieve_and_generate` against the
Knowledge Base.

"No pyproject.toml here; will be added if a dependency beyond boto3 is introduced at which point PythonFunction replaces Function for bundling. We just declared a dependency not packaging it".

## Options Considered

### Option A: Defer — SDK/console-only baseline
- **Pros:** Strictly minimal. Proves the retrieval pipeline works with zero
  additional services. Matches the "bare scaffold" philosophy most
  literally — nothing is added that isn't required to prove the KB itself
  functions.
- **Cons:** Not invocable by anything outside a local script or the AWS
  console — no integration point for any future consumer (a frontend, an
  agent, another service). Every later project built on this scaffold
  would need to add an invocation layer before it could be used for
  anything beyond manual testing.

### Option B: Include now — Lambda + API Gateway ← chosen
- **Pros:** Produces a genuinely usable artifact from commit 1 — an HTTP
  endpoint that can be called by a client, tested with `curl`, or wired
  into a demo, rather than only a set of provisioned AWS resources with no
  entry point. Establishes the invocation pattern (Lambda calling
  `RetrieveAndGenerate`) early, so later commits (auth, observability,
  guardrails) extend an existing interface rather than introducing one
  retroactively.
- **Cons:** Adds two service categories (compute + API layer) to a commit
  otherwise justified purely by "prove the KB works." The endpoint ships
  with no authentication or authorization in this commit — it is
  reachable by anyone with the URL until a later hardening commit adds an
  authorizer.

## Rejected Alternatives — Why Not

- **Why not defer to SDK/console-only:** This was the more defensible
  "minimal" answer, and I initially favored it. The reason to include the
  endpoint now instead: I explicitly asked for it, prioritizing having an
  invocable interface from commit 1 over the stricter minimalism of
  proving the pipeline via SDK calls alone. That is a legitimate
  engineering trade-off — usability of the artifact versus size of the
  commit — but it is worth being explicit that it *is* a trade-off, not a
  free choice. If asked "why does your baseline commit include an
  unauthenticated public endpoint," the honest answer is "I chose
  usability over strict minimalism at that stage, and authentication was
  deliberately deferred to a later, separately reviewable commit" — not
  "I didn't think about auth."

## Consequences

- **Positive:** The scaffold is testable end-to-end by anyone with the
  API URL, without needing AWS console/CLI access. Later commits (auth,
  rate limiting, WAF, observability) have a concrete existing surface to
  attach to, rather than needing to design the interface and the hardening
  simultaneously.
- **Negative / deferred cost:** The endpoint is unauthenticated and
  unmonitored until a later commit adds an authorizer and logging — this
  is a real, currently-open exposure, not a hypothetical one, for as long
  as this commit stands alone. Using an HTTP API (rather than REST API)
  trades some API Gateway features (e.g. request validation, usage plans)
  for lower cost and simpler setup — acceptable for a baseline, worth
  revisiting if those features become necessary.

## Revisit If

- The endpoint needs to be reachable by real (non-test) traffic before the
  authentication-hardening commit lands — at that point, the exposure
  window needs to be closed immediately, not deferred further.
- Request validation, custom domain names, or usage plans become necessary
  — HTTP API would need to be swapped for REST API, or those features
  added via alternate means.

## References

- Related: ADR 0001 (vector store selection), ADR 0003 (ingestion trigger
  strategy)