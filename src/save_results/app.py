import json
import os
from datetime import datetime

import boto3
import pymysql
import pymysql.cursors

dynamodb = boto3.resource('dynamodb')

JOB_STATE_TABLE = os.environ['JOB_STATE_TABLE']
RDS_ENDPOINT = os.environ.get('RDS_ENDPOINT', '')
RDS_DATABASE = os.environ.get('RDS_DATABASE', 'cmsc471results')
RDS_USERNAME = os.environ.get('RDS_USERNAME', 'cmsc471admin')
RDS_PASSWORD = os.environ.get('RDS_PASSWORD', '')

table = dynamodb.Table(JOB_STATE_TABLE)


def _rds_conn():
    return pymysql.connect(
        host=RDS_ENDPOINT,
        user=RDS_USERNAME,
        password=RDS_PASSWORD,
        database=RDS_DATABASE,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
    )


def lambda_handler(event, context):
    job_id = event['jobId']
    image_key = event.get('imageKey', '')
    extracted_text = event['extractedText']
    completed_at = datetime.utcnow().isoformat()

    # Write to DynamoDB (fast poll path)
    table.update_item(
        Key={'jobId': job_id},
        UpdateExpression='SET #s = :s, extractedText = :t, completedAt = :ts',
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={
            ':s': 'SUCCEEDED',
            ':t': extracted_text,
            ':ts': completed_at,
        },
    )

    # Write to RDS (durable record)
    if RDS_ENDPOINT:
        conn = _rds_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO results
                           (job_id, filename, extracted_text, status, created_at)
                       VALUES (%s, %s, %s, %s, %s)
                       ON DUPLICATE KEY UPDATE
                           extracted_text = VALUES(extracted_text),
                           status = VALUES(status)""",
                    (job_id, image_key, extracted_text, 'SUCCEEDED', completed_at),
                )
            conn.commit()
        finally:
            conn.close()

    return {'jobId': job_id, 'status': 'SUCCEEDED', 'extractedText': extracted_text}
