import json
import boto3
import os
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

INBOX_BUCKET = os.environ.get('INBOX_BUCKET')
JOB_STATE_TABLE = os.environ.get('JOB_STATE_TABLE')
table = dynamodb.Table(JOB_STATE_TABLE)

def lambda_handler(event, context):
    """
    Step Functions Step 1: Fetch image from S3
    """
    try:
        job_id = event['jobId']
        image_key = event['imageKey']
        
        # Update job status to FETCHING
        table.update_item(
            Key={'jobId': job_id},
            UpdateExpression='SET #status = :status, createdAt = :ts',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'FETCHING',
                ':ts': datetime.utcnow().isoformat()
            }
        )
        
        # Verify image exists in S3
        s3.head_object(Bucket=INBOX_BUCKET, Key=image_key)
        
        # Return image info for next step
        return {
            'jobId': job_id,
            'imageKey': image_key,
            'bucket': INBOX_BUCKET
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
