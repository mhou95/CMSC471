import json
import os

import boto3

dynamodb = boto3.resource('dynamodb')

JOB_STATE_TABLE = os.environ['JOB_STATE_TABLE']
table = dynamodb.Table(JOB_STATE_TABLE)

CORS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}


def lambda_handler(event, context):
    try:
        job_id = event['pathParameters']['id']

        resp = table.get_item(Key={'jobId': job_id})

        if 'Item' not in resp:
            return {
                'statusCode': 404,
                'headers': CORS,
                'body': json.dumps({'error': 'Job not found'}),
            }

        item = resp['Item']

        return {
            'statusCode': 200,
            'headers': {**CORS, 'Content-Type': 'application/json'},
            'body': json.dumps({
                'jobId': item['jobId'],
                'status': item.get('status', 'PROCESSING'),
                'extractedText': item.get('extractedText', ''),
                'createdAt': item.get('createdAt'),
            }),
        }

    except Exception as e:
        print(f'Error: {e}')
        return {
            'statusCode': 500,
            'headers': CORS,
            'body': json.dumps({'error': str(e)}),
        }
