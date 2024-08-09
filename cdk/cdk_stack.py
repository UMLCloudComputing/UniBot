from aws_cdk import (
    Stack,
    aws_bedrock as bedrock,
    aws_iam as iam,
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
        self.agent_name = kwargs.get('agent_name')

        bucket=s3.Bucket(
            self, 
            id=f"bucketid{construct_id}", 
            bucket_name=f"infobucket{construct_id.lower()}" # Provide a bucket name here
        )

        knowledge_role = iam.CfnRole(self, "KnowledgeBaseRule",
            assume_role_policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "bedrock.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            },
            policies=[
                {
                    "policyName": "AmazonBedrockAgentPolicy",
                    "policyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "bedrock:ListFoundationModels",
                                    "bedrock:ListCustomModels",
                                    "bedrock:Retrieve",
                                    "bedrock:InvokeModel",
                                ],
                                "Resource": "*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": "secretsmanager:GetSecretValue",
                                "Resource": "*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "s3:GetObject",
                                    "s3:ListBucket",
                                    "s3:PutObject"
                                ],
                                "Resource": "*"
                            },
                        ],
                    },
                }
            ],
            role_name=f"KnowledgeBaseRole_{construct_id}",
        )

        cfn_knowledge_base = bedrock.CfnKnowledgeBase(self, "MyCfnKnowledgeBase",
            knowledge_base_configuration=bedrock.CfnKnowledgeBase.KnowledgeBaseConfigurationProperty(
                type="VECTOR",
                vector_knowledge_base_configuration=bedrock.CfnKnowledgeBase.VectorKnowledgeBaseConfigurationProperty(
                    embedding_model_arn="arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
                )
            ),
            name=f"KnowledgeBase{construct_id}",
            role_arn=knowledge_role.attr_arn,
            storage_configuration=bedrock.CfnKnowledgeBase.StorageConfigurationProperty(
                type="PINECONE",
                pinecone_configuration=bedrock.CfnKnowledgeBase.PineconeConfigurationProperty(
                    connection_string=os.getenv("PINECONE_URL"),
                    credentials_secret_arn=os.getenv("PINECONE_API_KEY"),
                    field_mapping=bedrock.CfnKnowledgeBase.PineconeFieldMappingProperty(
                        metadata_field="metadataField",
                        text_field="textField"
                    ),
                    namespace="namespace"
                ),
            ),
        )

        cfn_data_source = bedrock.CfnDataSource(self, "MyCfnDataSource",
            data_source_configuration=bedrock.CfnDataSource.DataSourceConfigurationProperty(
                s3_configuration=bedrock.CfnDataSource.S3DataSourceConfigurationProperty(bucket_arn=bucket.bucket_arn),
                type="S3"
            ),
            knowledge_base_id=cfn_knowledge_base.attr_knowledge_base_id,
            name=f"source{construct_id}",
        )

        table = dynamodb.TableV2(self, f"Table{construct_id}",
            partition_key=dynamodb.Attribute(name="SessionId", type=dynamodb.AttributeType.STRING),
            # sort_key=dynamodb.Attribute(name="timestamp", type=dynamodb.AttributeType.STRING)
        )
        
        dockerFunc = _lambda.DockerImageFunction(
            scope=self,
            id=f"ID{construct_id}",
            function_name=construct_id,
            environment= {
                "AWS_ID": os.getenv('AWS_ACCESS_KEY_ID'),
                "AWS_KEY": os.getenv('AWS_SECRET_ACCESS_KEY'),
                "DYNAMO_TABLE" : table.table_name,
                "DISCORD_PUBLIC_KEY" : os.getenv('DISCORD_PUBLIC_KEY'),
                "ID" : os.getenv('ID')
            },            
            code=_lambda.DockerImageCode.from_image_asset(
                directory="src"
            ),
            timeout=Duration.seconds(300)
        )

        api = apigateway.LambdaRestApi(self, f"API{construct_id}",
            handler=dockerFunc,
            proxy=True,
        )

        table.grant_read_write_data(dockerFunc)