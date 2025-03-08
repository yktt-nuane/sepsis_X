from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct

class SepsisXStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define Lambda Layer with the required packages
        twitter_layer = lambda_.LayerVersion(
            self, "TwitterBotLayer",
            code=lambda_.Code.from_asset("lambda_layer"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            description="Layer containing tweepy and pytz for Twitter posting",
        )

        # Create IAM Role for Lambda with permissions to access Secrets Manager
        twitter_lambda_role = iam.Role(
            self, "TwitterBotLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        # Create a policy to access the specific secret
        secret_arn = "arn:aws:secretsmanager:ap-northeast-1:438774532845:secret:twitter-api-keys-OlaaNC"
        twitter_lambda_role.add_to_policy(iam.PolicyStatement(
            actions=["secretsmanager:GetSecretValue"],
            resources=[secret_arn]
        ))

        # Define the Lambda function
        twitter_lambda = lambda_.Function(
            self, "TwitterBotFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambda"),
            handler="twitter_bot.lambda_handler",
            timeout=Duration.seconds(30),
            environment={
                "SECRET_ARN": secret_arn,
            },
            role=twitter_lambda_role,
            layers=[twitter_layer],
            description="Lambda function to post daily sepsis updates to Twitter/X",
        )

        # Schedule the Lambda to run daily at 10:00 AM Japan time (01:00 AM UTC)
        daily_schedule = events.Rule(
            self, "DailyTwitterBotSchedule",
            schedule=events.Schedule.cron(
                minute="0",
                hour="1",  # 10:00 AM JST = 01:00 AM UTC
                month="*",
                week_day="*",
                year="*",
            ),
            description="Trigger for daily Twitter posts about sepsis at 10:00 AM JST",
        )

        # Add the Lambda function as a target for the scheduled event
        daily_schedule.add_target(targets.LambdaFunction(twitter_lambda))
