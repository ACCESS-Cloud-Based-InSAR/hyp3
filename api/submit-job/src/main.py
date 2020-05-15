import json
from os import environ

import boto3

BATCH_CLIENT = boto3.client('batch')


def lambda_handler(event, context):
    parameters = json.loads(event['body'])
    job = BATCH_CLIENT.submit_job(
        jobName=parameters['granule'],
        jobQueue=environ['JOB_QUEUE'],
        jobDefinition=environ['JOB_DEFINITION'],
        parameters=parameters
    )
    response_body = {
        'jobId': job['jobId'],
        'jobName': job['jobName']
    }
    return {
        'statusCode': 200,
        'body': json.dumps(response_body)
    }