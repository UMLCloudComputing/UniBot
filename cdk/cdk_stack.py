from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    Duration,
    aws_dynamodb as dynamodb,
)
from constructs import Construct
import os

from dotenv import load_dotenv
load_dotenv()

class CdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = dynamodb.TableV2(self, f"Table-{construct_id}",
            table_name=f"{construct_id}",
            partition_key=dynamodb.Attribute(name="SessionId", type=dynamodb.AttributeType.STRING),
            # sort_key=dynamodb.Attribute(name="timestamp", type=dynamodb.AttributeType.STRING)
        )
        
        dockerFunc = _lambda.DockerImageFunction(
            scope=self,
            id=f"Lambda-{construct_id}",
            function_name=construct_id,
            environment= {
                "DYNAMO_TABLE" : table.table_name,
                "DISCORD_PUBLIC_KEY" : os.getenv('DISCORD_PUBLIC_KEY'),
                "ID" : os.getenv('ID'),
                "INDEX_NAME" : os.getenv('INDEX_NAME'),
                "PINECONE_API_KEY" : os.getenv('PINECONE_API_KEY'),
                "OPENAI_API_KEY" : os.getenv('OPENAI_API_KEY'),
            },            
            code=_lambda.DockerImageCode.from_image_asset(
                directory="src"
            ),
            timeout=Duration.seconds(300)
        )

        api = apigateway.LambdaRestApi(self, f"API-{construct_id}",
            handler=dockerFunc,
            proxy=True,
        )

        table.grant_read_write_data(dockerFunc)