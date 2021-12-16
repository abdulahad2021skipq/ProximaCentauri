def lambda_handler(event,context):
    return 'Hello {} {}'.format(event['first_name'],event['last_name'])