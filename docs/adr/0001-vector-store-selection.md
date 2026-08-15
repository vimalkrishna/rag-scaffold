# S3 Vectors vs OpenSearch vs Aurora
# ADR 0001: Vector Store Selection for RAG Baseline

**Status:** Accepted

**Date:** 15.08.2026

**Commit:** [commit hash that introduces VectorBucket/CfnIndex]

## Context

The baseline RAG scaffold (`rag-scaffold` repo) is scoped deliberately narrow:
essential AWS services only, no domain logic, no VPC, no governance or
observability layered in yet, those arrive in separate, later commits.
Bedrock Knowledge Bases require a vector store backend, and AWS supports
several (OpenSearch Serverless, OpenSearch Managed Cluster, Aurora
PostgreSQL + pgvector, Pinecone, MongoDB Atlas, Neptune Analytics, S3
Vectors). The choice had to satisfy the baseline's own stated constraint
minimal infrastructure footprint, while remaining defensible under
interview-style questioning about why the "standard" choice (OpenSearch)
was not used.

## Decision

Use **Amazon S3 Vectors** as the vector store for the baseline Bedrock
Knowledge Base, via the native `S3_VECTORS` storage configuration on
`CfnKnowledgeBase`, backed by an `aws_s3vectors.CfnVectorBucket` and
`CfnIndex`.

## Options Considered

### Option A: Amazon OpenSearch Serverless
- **Pros:** The AWS-canonical backend for Bedrock Knowledge Bases most
  reference architectures default to it. Supports hybrid (semantic +
  keyword) search and the richest metadata filtering of the three options.
  Proven at large scale with consistent sub-second latency.
- **Cons:** Requires provisioning a collection plus three separate security
  policies (network, encryption, data access) before Bedrock can use it,
  the heaviest setup of the three. Bills a minimum OCU (OpenSearch Compute
  Unit) floor even at zero traffic, so idle cost is nonzero regardless of
  usage.

### Option B: Aurora PostgreSQL Serverless v2 + pgvector
- **Pros:** Familiar relational/SQL paradigm. Vector search can be joined
  against relational metadata in the same query. Cheaper than OpenSearch
  at idle, and reusable for non-vector data if the project grows that
  direction.

- **Cons:** Requires a VPC, subnets, security groups, route tables which
  contradicts the baseline's "no domain logic, essential services only"
  scope. Less common as a Bedrock KB backend in practice, so it's a harder
  default to justify without a concrete relational-query need this project
  doesn't have.

### Option C: Amazon S3 Vectors ← chosen
- **Pros:** No VPC, no idle provisioned capacity, pure pay-per-use.
  Reuses S3, which the scaffold already needs for source documents, so it
  adds no new service category. Offers up to 90% reduction in vector upload, storage, and query costs compared to traditional vector databases. 
  Infrequent queries return results in under one second, with frequent queries resulting in latencies as low as 100 milliseconds, 
  and a single index scales to two billion vectors. 
  Now natively supported in CDK `aws_s3vectors.CfnVectorBucket` /
  `CfnIndex`, and `CfnKnowledgeBase.S3VectorsConfigurationProperty` no
  custom resources or third-party construct packages required.

- **Cons:** Supports up to 1 KB of custom metadata and 35 metadata keys per vector, 
  narrower than OpenSearch's filter/hybrid feature set. Newer service GA'd
  from preview within roughly the past year, so it carries less production
  track record than OpenSearch.

## Rejected Alternatives, Why Not

- **Why not OpenSearch Serverless:** It is the safest, most "expected"
  answer, and I'm choosing against expectation deliberately. The baseline's
  explicit design goal is a minimal-footprint scaffold with governance and
  hardening deferred to later commits. OpenSearch's mandatory security-policy
  configuration and nonzero idle cost are exactly the kind of complexity
  this commit is meant to exclude, they belong closer to a "production
  readiness" commit than a "prove the pipeline works" commit.

- **Why not Aurora + pgvector:** The VPC requirement is disqualifying at
  this stage, not because VPCs are bad, but because networking setup is
  infrastructure the baseline hasn't earned yet, it has no security or
  compliance requirement driving it in commit 1. Introducing a VPC here
  would mean the "bare scaffold" already contains a decision that belongs
  to a later, deliberate networking/security commit.

## Consequences

- **Positive:** Baseline stays genuinely minimal, no VPC, no idle billing,
  one fewer service category to operate and explain. CDK support is native,
  so no dependency on external/preview construct libraries that could
  break or require migration later (see the `cdk-s3-vectors` community
  package, explicitly maintained only until AWS ships native support,
  which it now has).

- **Negative / deferred cost:** Metadata filtering ceiling (1 KB / 35 keys)
  may become a real constraint once domain-specific projects (e.g. the
  compliance-research-assistant) need richer filtering, that's a decision
  for that project's own ADR, not this one. Less production track record
  than OpenSearch means less external validation to point to if maturity
  is challenged directly.

## Revisit If

- A downstream project (e.g. compliance-research-assistant) needs hybrid
  semantic+keyword search or metadata filtering beyond S3 Vectors' limits.
- Query volume or latency requirements exceed what S3 Vectors' published
  figures support for the workload in question.
- AWS deprecates or materially changes S3 Vectors' Bedrock KB integration.

## References

- AWS: "Using S3 Vectors with Amazon Bedrock Knowledge Bases", AWS documentation
- AWS News Blog: "Introducing Amazon S3 Vectors" (preview announcement)
- AWS What's New: "Amazon S3 Vectors expands to 17 additional AWS Regions" (03-2026) total 31.
- Related: ADR 0002 (query interface), ADR 0003 (ingestion trigger strategy)