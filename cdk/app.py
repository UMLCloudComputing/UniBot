#!/usr/bin/env python3
import os
import aws_cdk as cdk
from dotenv import load_dotenv

load_dotenv()

from cdk_stack import CdkStack


app = cdk.App()
CdkStack(app, os.getenv('APP_NAME'))
app.synth()
