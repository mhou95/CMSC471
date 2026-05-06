import json
import boto3
import os
from datetime import datetime

textract = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')

JOB_STATE_TABLE = os.environ.get('JOB_STATE_TABLE')
table = dynamodb.Table(JOB_STATE_TABLE)

def lambda_handler(event, context):
    """
    Step Functions Step 2: Call Amazon Textract for text extraction
    """
    try:
        job_id = event['jobId']
        image_key = event['imageKey']
        bucket = event['bucket']
        
        # Update job status to PROCESSING
        table.update_item(
            Key={'jobId': job_id},
            UpdateExpression='SET #status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': 'PROCESSING'}
        )
        
        # Call Textract
        response = textract.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': image_key
                }
            }
        )
        
        # Extract text from response
        extracted_text = ''
        for item in response.get('Blocks', []):
            if item['BlockType'] == 'LINE':
                extracted_text += item['Text'] + '\n'
        
        # Return for next step
        return {
            'jobId': job_id,
            'imageKey': image_key,
            'extractedText': extracted_text
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
