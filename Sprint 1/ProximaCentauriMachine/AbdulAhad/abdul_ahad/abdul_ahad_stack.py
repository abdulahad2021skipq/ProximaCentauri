from aws_cdk import (
    aws_events_targets as targets_,
    core as cdk,
    aws_lambda as lambda_,
    aws_events as events_,
    aws_iam,
    aws_cloudwatch as cloudwatch

)
from resources import constants as constants
class AbdulAhadStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        lambda_role=self.create_lambda_role()
        webhealth_lambda=self.create_lambda('HelloLambda', './resources', 'webhealth_lambda.lambda_handler',lambda_role)
        
        
        lambda_schedule=events_.Schedule.rate(cdk.Duration.minutes(1))
        lambda_target=targets_.LambdaFunction(handler=webhealth_lambda)
        rule=events_.Rule(self, "Webhealth", description="Periodic Lambda analysis", enabled=True, schedule=lambda_schedule, targets=[lambda_target])

        
        
        
    def create_lambda_role(self):
        lambdaRole=aws_iam.Role(self, "lambda-role",
            assumed_by=aws_iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                               aws_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
                               aws_iam.ManagedPolicy.from_aws_managed_policy_name('CloudwatchFullAccess')
                               ])
        return lambdaRole
        
    def create_lambda(self, id, asset, handler,role):
        return lambda_.Function(self, id,
        code=lambda_.Code.from_asset(asset),
        runtime=lambda_.Runtime.PYTHON_3_6,
        handler=handler,
        role=role
       
        )