# lambda/query/handler.py
import json
import os

import boto3

# Created once per execution environment, reused across warm invocations —
# not per-request. Creating a boto3 client inside the handler function
# would rebuild it on every single call, adding latency for no benefit.
bedrock_agent_runtime = boto3.client("bedrock-agent-runtime")

KNOWLEDGE_BASE_ID = os.environ["KNOWLEDGE_BASE_ID"]
MODEL_ARN = os.environ["MODEL_ARN"]


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        question = body.get("question")

        if not question:
            return _response(400, {"error": "Request body must include 'question'"})

        result = bedrock_agent_runtime.retrieve_and_generate(
            input={"text": question},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                    "modelArn": MODEL_ARN,
                },
            },
        )

        return _response(200, {
            "answer": result["output"]["text"],
            "sessionId": result["sessionId"],
            "citations": _extract_citations(result.get("citations", [])),
        })

    except bedrock_agent_runtime.exceptions.ResourceNotFoundException:
        return _response(404, {"error": "Knowledge base not found"})
    except Exception as exc:
        # Baseline-level catch: logs the real error to CloudWatch for
        # diagnosis, returns a generic message so internals aren't leaked
        # to the caller. Narrower exception handling is a hardening-commit
        # task, not a baseline one — see notes below.
        print(f"Unhandled error: {exc}")
        return _response(500, {"error": "Internal error processing request"})


def _extract_citations(citations):
    return [
        {
            "text": ref.get("content", {}).get("text"),
            "location": ref.get("location"),
        }
        for citation in citations
        for ref in citation.get("retrievedReferences", [])
    ]


def _response(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body_dict),
    }