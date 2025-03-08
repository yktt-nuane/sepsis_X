#!/usr/bin/env python3
import os
import aws_cdk as cdk
from sepsis_x.sepsis_x_stack import SepsisXStack

app = cdk.App()

# Environment variables from .env file
account = os.getenv('AWS_ACCOUNT_ID')
region = os.getenv('AWS_REGION', 'ap-northeast-1')

SepsisXStack(
    app,
    "SepsisXStack",
    env=cdk.Environment(account=account, region=region),
    description="CDK stack for daily X (Twitter) posts about sepsis data"
)

app.synth()
