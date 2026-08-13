
from aws_cdk import Stack
from constructs import Construct


class RagScaffoldStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Resources added incrementally, one ADR-backed decision at a time.
