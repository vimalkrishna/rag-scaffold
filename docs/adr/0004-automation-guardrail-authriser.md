# Ingestion Automation, Guardrails, authoriser
# ADR 0004: Ingestion Automation (S3 Event → StartIngestionJob)

**Status:** Proposed

**Date:** 15-08-2026 (opened as placeholder decision deferred)

**Commit:** [to be filled in when this ADR moves to Accepted]

## Context

ADR 0003 established manual `StartIngestionJob` invocation as a
deliberate, temporary choice for the baseline commit made specifically
to force direct, firsthand understanding of ingestion job mechanics before
any automation abstracts that away. ADR 0003 also stated explicitly that
automatic triggering (S3 event → Lambda → `StartIngestionJob`) is the
better design for anything beyond learning, and is expected once the
fundamentals are proven. This ADR exists to record that the automation
step was planned from the outset, not bolted on reactively, and to give it
its own reviewable commit rather than folding it into a later, larger
change.

## Decision

_Not yet made. To be filled in when this work starts._

Expected shape, not yet decided in detail: an S3 event notification
(likely `s3:ObjectCreated:*` on the document bucket) invoking a Lambda
function that calls `StartIngestionJob` against the existing Knowledge
Base data source, with some form of debounce/batching to avoid firing a
separate job per object when documents are uploaded in bulk.

## Options Considered

_To be filled in when this ADR is picked up at minimum, evaluate:_
- S3 Event Notifications → Lambda direct
- S3 Event Notifications → SQS (batching/debounce) → Lambda
- EventBridge rule on S3 events → Lambda
- Scheduled (EventBridge Scheduler) periodic sync instead of event-driven

## Rejected Alternatives Why Not

_To be filled in 

## Consequences

_To be filled in._

## Revisit If

_To be filled in._

## References

- ADR 0003 (ingestion trigger strategy) this ADR is the deferred
  