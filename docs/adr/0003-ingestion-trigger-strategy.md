# Manual StartIngestionJob, not S3-event-driven
# ADR 0003: Ingestion Trigger Strategy for RAG Baseline

**Status:** Accepted

**Date:** 14-08-2026

**Commit:** [the commit that establishes the data source / first manual ingestion run]

## Context

Once documents land in the S3 bucket, Bedrock Knowledge Bases do not
automatically embed and index them an ingestion job (`StartIngestionJob`)
must be triggered to sync the data source into the vector store. That
trigger can be automated (e.g. an S3 event firing a Lambda that calls
`StartIngestionJob`) or invoked manually (CLI, console, or a one-off
script) by whoever is operating the pipeline. The baseline scaffold's
purpose is not only to produce working infrastructure but to be understood
at a first-principles level every service's role needs to be explainable,
including to someone testing fundamentals rather than depth. That goal
directly shaped this decision, more than any cost or architecture
trade-off did.

## Decision

Trigger ingestion **manually** in this baseline `StartIngestionJob` is
called out-of-band (CLI/console/script), with no S3-event automation wired
in this commit.

## Options Considered

### Option A: Automatic S3 event → Lambda → StartIngestionJob
- **Pros:** Matches how a real production pipeline would behave documents
  land, ingestion happens without operator intervention. Removes a manual
  step that would otherwise need to be remembered every time new content
  is added. Natural fit once the pipeline is trusted and stable.
- **Cons:** Wraps the actual API call (`StartIngestionJob`) inside an event
  trigger from the first commit, which means the mechanics of ingestion what a sync job does, how long it takes, what "in progress" vs
  "complete" looks like, what staleness means for retrieval are never
  directly observed by the person building the system. The automation
  becomes something to trust rather than something understood.

### Option B: Manual operator calls StartIngestionJob directly ← chosen
- **Pros:** Forces direct interaction with the ingestion API before any
  automation hides it. Makes ingestion latency, job status, and sync
  staleness visible and concrete rather than abstracted away. Keeps the
  baseline commit free of an additional Lambda + event-source mapping,
  consistent with the scaffold's minimal-footprint scope.
  
- **Cons:** Not representative of how the finished system will actually
  run someone reading only this commit would need to know that
  automation is coming later, or they'd reasonably assume manual ingestion
  is the permanent design. Requires the operator to remember to trigger
  ingestion after every document change, which does not scale past a
  learning/demo context.

## Rejected Alternatives Why Not

- **Why not automatic (S3 event trigger):** This is the objectively better
  design for anything beyond learning and I would default to it for any
  of the five downstream projects (e.g. compliance-research-assistant)
  once the fundamentals are proven. It's rejected here specifically
  because automating the trigger before understanding what it triggers
  would mean the ingestion mechanics job lifecycle, sync semantics,
  what "stale" means for a RAG system's answers get learned secondhand
  from documentation instead of firsthand from calling the API myself.
  That trade-off is only defensible in a baseline/learning commit; it
  would not be defensible as a permanent choice in a production system,
  and this ADR should not be read as an argument against automating
  ingestion generally.

## Consequences

- **Positive:** Direct, hands-on understanding of `StartIngestionJob`
  behavior job states, duration, and what triggers a re-embed before
  any of that is abstracted behind an event trigger. No additional Lambda,
  IAM role, or event-source mapping in this commit.

- **Negative / deferred cost:** The pipeline is not self-sustaining new
  or changed documents in S3 do not appear in retrieval results until
  ingestion is triggered manually. This is a real functional gap for
  anyone other than the operator running the scaffold, not just a
  cosmetic simplification, and it must be closed before the scaffold is
  used as a base for any of the five domain-specific projects.

## Revisit If

- Moving from this scaffold to a domain-specific project (e.g.
  compliance-research-assistant) where content updates are expected to
  happen without operator supervision.
- The manual step is forgotten often enough in practice that stale
  retrieval results become a recurring problem even during learning/demo
  use at that point, automate immediately rather than tolerating it
  further.

## References

- Related: ADR 0001 (vector store selection), ADR 0002 (query interface)