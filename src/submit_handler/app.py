import json
import os
import uuid

import boto3

stepfunctions = boto3.client('stepfunctions')

STATE_MACHINE_ARN = os.environ['STATE_MACHINE_ARN']

CORS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body') or '{}')
        image_key = body.get('imageKey')

        if not image_key:
            return {
                'statusCode': 400,
                'headers': CORS,
                'body': json.dumps({'error': 'imageKey is required'}),
            }

        job_id = str(uuid.uuid4())

        resp = stepfunctions.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            name=job_id,
            input=json.dumps({'jobId': job_id, 'imageKey': image_key}),
        )

        return {
            'statusCode': 200,
            'headers': {**CORS, 'Content-Type': 'application/json'},
            'body': json.dumps({'jobId': job_id, 'executionArn': resp['executionArn']}),
        }

    except Exception as e:
        print(f'Error: {e}')
        return {
            'statusCode': 500,
            'headers': CORS,
            'body': json.dumps({'error': str(e)}),
        }
