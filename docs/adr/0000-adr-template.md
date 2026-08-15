# template to force a "Rejected Alternatives"
# ADR 0000: Template

**Status:** [Proposed | Accepted | Superseded by ADR-XXXX]

**Date:** DD-MM-YYYY

**Commit:** [commit hash or PR link this decision belongs to]

## Context

What problem or constraint forced this decision? State the goal being served
(e.g. "baseline RAG scaffold must have no domain logic, minimal services,
no VPC") — not just the technical question, but why it mattered right now.

## Decision

The choice made, stated in one or two sentences. No hedging — this is the
thing you'd say out loud if asked "what did you pick and why."

## Options Considered

List every option that was genuinely on the table, including the one you
picked. For each:

### Option A: [name]
- **Pros:**

- **Cons:**

### Option B: [name]
- **Pros:**

- **Cons:**

### Option C: [name] ← chosen
- **Pros:**

- **Cons:**

## Rejected Alternatives — Why Not

For every option NOT chosen, write the specific reason it lost — in your own
words, not a restatement of the "Cons" above. This is the section that gets
tested in an interview: "why didn't you use X" should have an answer here,
not something you improvise on the spot.

- **Why not [Option A]:**

- **Why not [Option B]:**

## Consequences

What does this decision commit you to? What does it foreclose or make
harder later? Be honest about trade-offs you're accepting, not just ones
you're avoiding.

- Positive:
- Negative / deferred cost:

## Revisit If

Concrete conditions under which this decision should be reopened (e.g.
"if S3 Vectors metadata limits block a required filter," "if query volume
exceeds N req/s and latency becomes unacceptable"). If you can't name a
condition, that's worth noticing — it may mean the decision wasn't actually
contingent on anything, or you haven't thought through its limits yet.

## References

- Links to docs, benchmarks, or search results that informed the decision
- Related ADRs