import json
import boto3
import os
import uuid
import base64

s3 = boto3.client('s3')

INBOX_BUCKET = os.environ.get('INBOX_BUCKET')

CORS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
}


def lambda_handler(event, context):
    method = event.get('httpMethod', 'POST')

    try:
        if method == 'POST':
            return _upload(event)
        elif method == 'GET':
            return _list()
        elif method == 'DELETE':
            return _delete(event)
        return {'statusCode': 405, 'headers': CORS, 'body': json.dumps({'error': 'Method not allowed'})}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'headers': CORS, 'body': json.dumps({'error': str(e)})}


def _upload(event):
    """
    Accepts either:
      - JSON body: {"filename": "foo.jpg", "data": "<base64>"}
      - Raw binary body (isBase64Encoded: true from API Gateway binary passthrough)
    """
    body_raw = event.get('body', '')
    is_b64 = event.get('isBase64Encoded', False)

    # Try JSON wrapper first
    try:
        parsed = json.loads(body_raw)
        file_name = parsed.get('filename', f"upload-{uuid.uuid4()}.jpg")
        file_bytes = base64.b64decode(parsed['data'])
    except Exception:
        # Fall back to raw binary passthrough
        if not body_raw:
            return {'statusCode': 400, 'headers': CORS,
                    'body': json.dumps({'error': 'No file data in request body'})}
        file_bytes = base64.b64decode(body_raw) if is_b64 else body_raw.encode()
        params = event.get('queryStringParameters') or {}
        file_name = params.get('filename', f"upload-{uuid.uuid4()}.jpg")

    s3.put_object(Bucket=INBOX_BUCKET, Key=file_name, Body=file_bytes)

    return {
        'statusCode': 200,
        'headers': {**CORS, 'Content-Type': 'application/json'},
        'body': json.dumps({'objectKey': file_name, 'bucket': INBOX_BUCKET}),
    }


def _list():
    response = s3.list_objects_v2(Bucket=INBOX_BUCKET)
    files = [obj['Key'] for obj in response.get('Contents', [])]
    return {
        'statusCode': 200,
        'headers': {**CORS, 'Content-Type': 'application/json'},
        'body': json.dumps({'files': files}),
    }


def _delete(event):
    key = event['pathParameters']['key']
    s3.delete_object(Bucket=INBOX_BUCKET, Key=key)
    return {'statusCode': 204, 'headers': CORS, 'body': '{}'}
