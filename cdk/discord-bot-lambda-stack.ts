import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import 'dotenv/config';

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
        timeout: cdk.Duration.seconds(10),
        architecture: lambda.Architecture.X86_64,
        environment: {
          DISCORD_PUBLIC_KEY: process.env.DISCORD_PUBLIC_KEY ?? (() => { throw new Error("DISCORD_PUBLIC_KEY is not set"); })(),
          BEDROCK_ID: process.env.BEDROCK_ID ?? (() => { throw new Error("BEDROCK_ID is not set"); })(),
          BEDROCK_KEY: process.env.BEDROCK_KEY ?? (() => { throw new Error("BEDROCK_KEY is not set"); })()
        },
      }
    );

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
  }
}
