from aws_cdk import (
    aws_events_targets as targets_,
    core as cdk,
    aws_lambda as lambda_,
    aws_events as events_,
    aws_iam,
    aws_cloudwatch as cloudwatch_,
    aws_sns as sns,
    aws_cloudwatch_actions as actions_,
    aws_sns_subscriptions as subscriptions_
    

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
        
        topic = sns.Topic(self, "websitelife")
        topic.add_subscription(subscriptions_.EmailSubscription("abdul.ahad.shams.s@skipq.org"))
        
        
        dimension={'URL':constants.URL_TO_MONITOR}
        availability_Metric=cloudwatch_.Metric(metric_name=constants.URL_MONITOR_NAME_AVAILABILITY , 
        namespace=constants.URL_MONITOR_NAMESPACE, 
        dimensions_map=dimension)
        
        availability_alarm=cloudwatch_.Alarm(self, id="Availability alarm", 
        metric=availability_Metric,
        comparison_operator=cloudwatch_.ComparisonOperator.LESS_THAN_THRESHOLD, 
        threshold=1, 
        datapoints_to_alarm=1, 
        evaluation_periods=1,
        period=cdk.Duration.minutes(1)
        )
        
        dimension={'URL':constants.URL_TO_MONITOR}
        Latency_Metric=cloudwatch_.Metric(metric_name=constants.URL_MONITOR_NAME_LATENCY , 
        namespace=constants.URL_MONITOR_NAMESPACE, 
        dimensions_map=dimension)
        
        Latency_alarm=cloudwatch_.Alarm(self, id="Latency alarm", 
        metric=Latency_Metric,
        comparison_operator=cloudwatch_.ComparisonOperator.GREATER_THAN_THRESHOLD, 
        threshold=1, 
        datapoints_to_alarm=1, 
        evaluation_periods=1,
        period=cdk.Duration.minutes(1)
        )
        
        availability_alarm.add_alarm_action(actions_.SnsAction(topic))
        Latency_alarm.add_alarm_action(actions_.SnsAction(topic))
        
        
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