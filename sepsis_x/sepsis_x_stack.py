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

        # Define the Lambda function for Twitter posts
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
            description="Lambda function to post daily sepsis and ARDS updates to Twitter/X",
        )

        # Schedule the Lambda to run daily at 10:00 AM Japan time (01:00 AM UTC) for Sepsis posts
        sepsis_schedule = events.Rule(
            self, "DailySepsisBotSchedule",
            schedule=events.Schedule.cron(
                minute="0",
                hour="1",  # 10:00 AM JST = 01:00 AM UTC
                month="*",
                week_day="*",
                year="*",
            ),
            description="Trigger for daily Twitter posts about sepsis at 10:00 AM JST",
        )

        # Schedule the Lambda to run daily at 10:30 AM Japan time (01:30 AM UTC) for ARDS posts
        ards_schedule = events.Rule(
            self, "DailyARDSBotSchedule",
            schedule=events.Schedule.cron(
                minute="30",
                hour="1",  # 10:30 AM JST = 01:30 AM UTC
                month="*",
                week_day="*",
                year="*",
            ),
            description="Trigger for daily Twitter posts about ARDS at 10:30 AM JST",
        )

        # Add the Lambda function as a target for the sepsis scheduled event
        sepsis_schedule.add_target(
            targets.LambdaFunction(
                twitter_lambda,
                event=events.RuleTargetInput.from_object({"post_type": "sepsis"})
            )
        )
        
        # Add the Lambda function as a target for the ARDS scheduled event
        ards_schedule.add_target(
            targets.LambdaFunction(
                twitter_lambda,
                event=events.RuleTargetInput.from_object({"post_type": "ards"})
            )
        )