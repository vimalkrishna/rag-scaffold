# 8-step verification plan — rag-scaffold baseline

**Purpose:** This is a scaffold project with falsifiability claim. It confirms each of the seven services functions correctly, isolated
by layer, so that a failure at any single step narrows the fault to a
specific boundary rather than "something's wrong somewhere." Each step
states an expected result before it's run this is what makes the check
falsifiable rather than a plausibility scan.

We verify `uv run cdk deploy` succeeds. Re-run in full whenever this
repo is cloned as the starting point for a new project.

---

## Step 1 — Verify document landed in S3

**Layer:** Console

**Action:** Open the document bucket in the S3 console after uploading a
test file.

**Expected:** The object appears in the bucket listing with the correct
size and a recent timestamp.

**Evidence:** Screenshot of the object list.

---

## Step 2 — Verify S3 Vector bucket and index

**Layer:** CLI

**Action:**
```bash
aws s3vectors get-index --vector-bucket-name <name> --index-name rag-scaffold-index
```
**Expected:** Output shows `dimension: 1024`, `distanceMetric: cosine`,
and a status indicating the index is active.

**Evidence:** Screenshot of terminal output.

**Note:** Console support for S3 Vectors may be partial — CLI is the
reliable source of truth here, not a fallback.

---

## Step 3 — Trigger and verify ingestion job

**Layer:** Console

**Action:** Bedrock Knowledge Base → Data source → Sync. Wait for
completion.

**Expected:** Sync history table shows status `COMPLETE` with a
non-zero document count matching what's in the S3 bucket.

**Evidence:** Screenshot of the sync history table.

**Note:** This step is manual by design see ADR 0003. If status shows
`COMPLETE` with 0 documents, that's a distinct, diagnosable failure from
`FAILED` — record which one occurred, not just "sync didn't work."

---

## Step 4 — Test retrieval directly in the Knowledge Base console

**Layer:** Console

**Action:** Bedrock Knowledge Base → Test Knowledge Base panel. Ask a
question the uploaded document can answer.

**Expected:** Retrieved source chunks reference the correct document, and
the generated answer is factually consistent with it.

**Evidence:** Screenshot of both the retrieved chunks and the generated
answer.

**Why this step matters:** Isolates embedding + vector store + KB
correctness *before* Lambda or API Gateway are in the loop. If this step
fails, the fault is upstream of any code you wrote.

---

## Step 5 — Review IAM role permissions

**Layer:** Console

**Action:** IAM → open the Knowledge Base role and the Lambda execution
role.

**Expected:** Trust relationships show the correct assumed-by principal
for each; permissions match what's declared in the CDK stack (no
broader wildcard actions than intended).

**Evidence:** Screenshot of Trust relationships tab and Permissions tab
for each role.

**Note:** This is also where you verify whether the `s3vectors:*`
wildcard flagged in the stack code has been scoped down yet.

---

## Step 6 — Test the Lambda function in isolation

**Layer:** Console

**Action:** Lambda → Test tab. Use a mock API Gateway proxy-integration
event as the payload.

**Expected:** Execution succeeds (no error), and the response body
contains a generated answer.

**Evidence:** Screenshot of the execution result and the linked
CloudWatch log.

**Why this step matters:** Confirms Lambda → Bedrock wiring works
independent of API Gateway. If step 7 fails but this passes, the fault
is isolated to the HTTP layer.

---

## Step 7 — Test the API Gateway endpoint end-to-end

**Layer:** CLI

**Action:**
```bash
curl -X POST <api-url>/query -d '{"question": "..."}'
```

**Expected:** HTTP 200, response body containing a generated answer
consistent with step 4's result.

**Evidence:** Screenshot of terminal showing status code and response
body.

**Why CLI, not console:** API Gateway HTTP APIs have no console
"invoke and view response" feature — this is the only layer that tests
the system the way an actual external caller experiences it.

---

## Step 8 — Full round-trip freshness check

**Layer:** Console + CLI

**Action:** Upload a new or modified document to S3. Manually re-trigger
ingestion (step 3). Re-call the API endpoint (step 7) with a question
only the new content answers.

**Expected:** The step-7 response reflects the new content; a question
about the new document fails or gives a stale answer if asked *before*
re-ingestion, and succeeds *after*.

**Evidence:** Screenshot of the before/after responses side by side.

**Why this step matters:** This is the only step that tests the whole
chain together, and it's the one that makes ADR 0003's "staleness until
re-synced" claim checkable rather than theoretical.

---

## Reading the results

Two steps testing the same underlying call from different layers (4 vs.
6, and by extension 6 vs. 7) is deliberate — if the console test in step
4 passes but the CLI test in step 7 fails, the fault is narrowed to
Lambda or API Gateway, not Bedrock. 

Record **expected vs. actual** for
every step, not just pass/fail — "expected `COMPLETE` with 1 document,
got `COMPLETE` with 0" is a checkable, falsifiable record. "Sync ran" is
not.