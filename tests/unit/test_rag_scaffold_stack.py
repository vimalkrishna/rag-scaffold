import aws_cdk as cdk
from aws_cdk.assertions import Template

from rag_scaffold.rag_scaffold_stack import RagScaffoldStack


def test_stack_synthesizes():
    app = cdk.App()
    stack = RagScaffoldStack(app, "RagScaffoldStack")
    Template.from_stack(stack)
