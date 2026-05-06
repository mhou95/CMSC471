import json
import os

import boto3

s3 = boto3.client('s3')

STATIC_SITE_BUCKET = os.environ['STATIC_SITE_BUCKET']

CORS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}


def lambda_handler(event, context):
    try:
        # Derive the API base URL from the incoming request so we never need
        # a circular env-var reference back to the ApiGateway resource.
        rc = event.get('requestContext', {})
        domain = rc.get('domainName', '')
        stage = rc.get('stage', 'Prod')
        api_endpoint = f'https://{domain}/{stage}' if domain else ''

        response = s3.get_object(Bucket=STATIC_SITE_BUCKET, Key='index.html')
        html = response['Body'].read().decode('utf-8')

        # Inject the live API URL into the {{API_ENDPOINT}} placeholder so the
        # frontend JS never needs a hardcoded URL.
        html = html.replace('{{API_ENDPOINT}}', api_endpoint)

        return {
            'statusCode': 200,
            'headers': {**CORS, 'Content-Type': 'text/html'},
            'body': html,
        }
    except Exception as e:
        print(f'Error: {e}')
        return {
            'statusCode': 500,
            'headers': CORS,
            'body': json.dumps({'error': str(e)}),
        }
