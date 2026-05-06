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
        method = event.get('httpMethod', 'GET')

        if method == 'GET':
            resp = table.scan()
            records = [
                {
                    'jobId': item['jobId'],
                    'extractedText': item['extractedText'],
                    'createdAt': item.get('createdAt'),
                }
                for item in resp.get('Items', [])
                if item.get('extractedText')
            ]
            return {
                'statusCode': 200,
                'headers': {**CORS, 'Content-Type': 'application/json'},
                'body': json.dumps(records),
            }

        if method == 'DELETE':
            job_id = event['pathParameters']['id']
            table.delete_item(Key={'jobId': job_id})
            return {'statusCode': 204, 'headers': CORS, 'body': '{}'}

        return {
            'statusCode': 405,
            'headers': CORS,
            'body': json.dumps({'error': 'Method not allowed'}),
        }

    except Exception as e:
        print(f'Error: {e}')
        return {
            'statusCode': 500,
            'headers': CORS,
            'body': json.dumps({'error': str(e)}),
        }
