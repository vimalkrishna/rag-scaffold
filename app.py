#!/usr/bin/env python3
import aws_cdk as cdk

from rag_scaffold.rag_scaffold_stack import RagScaffoldStack

app = cdk.App()
RagScaffoldStack(app, "RagScaffoldStack")

app.synth()
