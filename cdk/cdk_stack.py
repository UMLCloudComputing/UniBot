from aws_cdk import (
    # Duration,
    Stack,
    aws_bedrock as bedrock,
    aws_iam as iam,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    Duration,
    CfnOutput
)
from constructs import Construct
import string
import random
import os

from dotenv import load_dotenv
load_dotenv()

base_prompt_template='''System: A chat between a curious User and an artificial intelligence Bot. The Bot gives helpful, detailed, and polite answers to the User's questions. In this session, the model has access to external functionalities.
To assist the user, you can reply to the user or invoke an action. Only invoke actions if relevant to the user request.
$instruction$

The following actions are available:$tools$
Model Instructions:
$model_instructions$
$conversation_history$
User: $question$
$thought$ $bot_response$'''

kb_template='''A chat between a curious User and an artificial intelligence Bot. The Bot gives helpful, detailed, and polite answers to the User's questions.

In this session, the model has access to search results and a user's question, your job is to answer the user's question using only information from the search results.

Model Instructions:
- You should provide concise answer to simple questions when the answer is directly contained in search results, but when comes to yes/no question, provide some details.
- In case the question requires multi-hop reasoning, you should find relevant information from search results and summarize the answer based on relevant information with logical reasoning.
- If the search results do not contain information that can answer the question, please state that you could not find an exact answer to the question, and if search results are completely irrelevant, say that you could not find an exact answer, then summarize search results.
- Remember to add a citation to the end of your response using markers like %[1]%, %[2]%, %[3]%, etc for the corresponding passage supports the response.
- DO NOT USE INFORMATION THAT IS NOT IN SEARCH RESULTS!

User: $query$ Bot:
Resources: Search Results: $search_results$ Bot:'''

class CdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.agent_name = kwargs.get('agent_name')

        bucket=s3.Bucket(
            self, 
            id="bucket123", 
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
                                "Action": "bedrock:InvokeModel",
                                "Resource": "*",
                            },
                            {
                                "Effect": "Allow",
                                "Action": "bedrock:Retrieve",
                                "Resource": "*",
                            },
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "bedrock:ListFoundationModels",
                                    "bedrock:ListCustomModels"
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

                    # the properties below are optional
                    namespace="namespace"
                ),
            ),

            # # the properties below are optional
            # description="description",
            # tags={
            #     "tags_key": "tags"
            # }
        )

        cfn_data_source = bedrock.CfnDataSource(self, "MyCfnDataSource",
            data_source_configuration=bedrock.CfnDataSource.DataSourceConfigurationProperty(
                s3_configuration=bedrock.CfnDataSource.S3DataSourceConfigurationProperty(
                    bucket_arn=bucket.bucket_arn,

                    # the properties below are optional
                    # bucket_owner_account_id="bucketOwnerAccountId",
                    # inclusion_prefixes=["inclusionPrefixes"]
                ),
                type="S3"
            ),
            knowledge_base_id=cfn_knowledge_base.attr_knowledge_base_id,
            name=f"source{construct_id}",

            # # the properties below are optional
            # data_deletion_policy="dataDeletionPolicy",
            # description="description",
            # server_side_encryption_configuration=bedrock.CfnDataSource.ServerSideEncryptionConfigurationProperty(
            #     kms_key_arn="kmsKeyArn"
            # ),
            # vector_ingestion_configuration=bedrock.CfnDataSource.VectorIngestionConfigurationProperty(
            #     chunking_configuration=bedrock.CfnDataSource.ChunkingConfigurationProperty(
            #         chunking_strategy="chunkingStrategy",

            #         # the properties below are optional
            #         fixed_size_chunking_configuration=bedrock.CfnDataSource.FixedSizeChunkingConfigurationProperty(
            #             max_tokens=123,
            #             overlap_percentage=123
            #         )
            #     )
            # )
        )

        cfn_role = iam.CfnRole(self, "AmazonBedrockAgentRole",
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
                                "Action": "bedrock:InvokeModel",
                                "Resource": "*",
                            },
                            {
                                "Effect": "Allow",
                                "Action": "bedrock:Retrieve",
                                "Resource": "*",
                            }
                        ],
                    },
                }
            ],
            role_name=f"AmazonBedrockAgentRole_{construct_id}",
        )

        cfn_agent = bedrock.CfnAgent(self, "Agent",
            agent_name=f"MyAgent{construct_id}",
            description='Production',
            agent_resource_role_arn= cfn_role.attr_arn,
            auto_prepare=True,
            foundation_model="amazon.titan-text-premier-v1:0",
            instruction="You are a chatbot for the University of Massachusetts Lowell. Your goal is to answer questions to the best of your ability. Please ask the user to clarify if necessary",
            knowledge_bases=[bedrock.CfnAgent.AgentKnowledgeBaseProperty(
                description="Pull information from here when user asks about the University of Massachusetts Lowell",
                knowledge_base_id=cfn_knowledge_base.attr_knowledge_base_id,

                # the properties below are optional
                # knowledge_base_state="knowledgeBaseState"
            )],
            prompt_override_configuration=bedrock.CfnAgent.PromptOverrideConfigurationProperty(
                prompt_configurations=[
                    bedrock.CfnAgent.PromptConfigurationProperty(
                        base_prompt_template=base_prompt_template,
                        inference_configuration=bedrock.CfnAgent.InferenceConfigurationProperty(
                            maximum_length=2048,
                            temperature=0,
                            top_p=0.1,
                        ),
                        prompt_creation_mode="OVERRIDDEN",
                        prompt_type="ORCHESTRATION"
                    ),

                    bedrock.CfnAgent.PromptConfigurationProperty(
                        base_prompt_template=kb_template,
                        inference_configuration=bedrock.CfnAgent.InferenceConfigurationProperty(
                            maximum_length=2048,
                            temperature=0,
                            top_p=0.1,
                        ),
                        prompt_creation_mode="OVERRIDDEN",
                        prompt_type="KNOWLEDGE_BASE_RESPONSE_GENERATION"
                    )
                ],
            ),
        )

        cfn_agent_alias = bedrock.CfnAgentAlias(self, f"MyCfnAgentAlias{construct_id}",
            agent_alias_name=f"Production{construct_id}",
            agent_id=cfn_agent.attr_agent_id,

            # # the properties below are optional
            # description="description",
            # routing_configuration=[bedrock.CfnAgentAlias.AgentAliasRoutingConfigurationListItemProperty(
            #     agent_version="agentVersion"
            # )],
            # tags={
            #     "tags_key": "tags"
            # }
        )
        
        dockerFunc = _lambda.DockerImageFunction(
            scope=self,
            id=f"ID{construct_id}",
            function_name=construct_id,
            environment= {
                "AGENT_ID": cfn_agent.attr_agent_id,
                "AGENT_ALIAS": cfn_agent_alias.attr_agent_alias_id,
                "AWS_ID": os.getenv('AWS_ACCESS_KEY_ID'),
                "AWS_KEY": os.getenv('AWS_SECRET_ACCESS_KEY'),
                "DYNAMO_TABLE" : os.getenv('DYNAMO_TABLE'),
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

        # CfnOutput(self, "Knowledge Base ID: ", value=cfn_knowledge_base.attr_knowledge_base_id)