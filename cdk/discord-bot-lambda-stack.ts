import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import 'dotenv/config';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

require('dotenv').config()

export class DiscordBotLambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const dockerFunction = new lambda.DockerImageFunction(
      this,
      "DockerFunction",
      {
        code: lambda.DockerImageCode.fromImageAsset("./src"),
        memorySize: 1024,
        timeout: cdk.Duration.seconds(600),
        architecture: lambda.Architecture.X86_64,
        environment: {
          DISCORD_PUBLIC_KEY: process.env.DISCORD_PUBLIC_KEY ?? (() => { throw new Error("DISCORD_PUBLIC_KEY is not set"); })(),
          BEDROCK_ID: process.env.BEDROCK_ID ?? (() => { throw new Error("BEDROCK_ID is not set"); })(),
          BEDROCK_KEY: process.env.BEDROCK_KEY ?? (() => { throw new Error("BEDROCK_KEY is not set"); })(),
          ID: process.env.ID ?? (() => { throw new Error("BEDROCK_KEY is not set"); })(),
          S3_ID: process.env.S3_ID ?? (() => { throw new Error("S3_ID is not set"); })(),
          S3_KEY: process.env.S3_KEY ?? (() => { throw new Error("S3_KEY is not set"); })(),
          AGENT_ALIAS: process.env.AGENT_ALIAS ?? (() => { throw new Error("AGENT_ALIAS is not set"); })(),
          AGENT_ID: process.env.AGENT_ID ?? (() => { throw new Error("AGENT_ID is not set"); })(),
          CITATION_BUCKET: process.env.CITATION_BUCKET ?? (() => { throw new Error("CITATION_BUCKET is not set"); })(),
          DYNAMO_ID: process.env.DYNAMO_ID ?? (() => { throw new Error("DYNAMO_ID is not set"); })(),
          DYNAMO_KEY: process.env.DYNAMO_KEY ?? (() => { throw new Error("DYNAMO_KEY is not set"); })(),
        },
      }
    );

    const api = new apigateway.LambdaRestApi(this, `InteractionsAPI${id}`, {
      handler: dockerFunction,
      proxy: true,
    });

    const functionUrl = dockerFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ["*"],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ["*"],
      },
    });

    new cdk.CfnOutput(this, "FunctionUrl", {
      value: functionUrl.url,
    });

    new cdk.CfnOutput(this, "ApiGatewayUrl", {
      value: api.url,
    }); 
  }
}
