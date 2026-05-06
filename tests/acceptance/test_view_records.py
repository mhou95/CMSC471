"""Acceptance tests: view and delete records via /api/records (Story S9)."""
import json
import uuid

import boto3
import pytest
import requests
from pytest_bdd import given, scenarios, then, when

scenarios('features/view_records.feature')


@given('the API is deployed', target_fixture='api_base')
def api_deployed(api_endpoint):
    return api_endpoint


@when('I GET "/api/records"', target_fixture='records_response')
def get_records(api_base):
    return requests.get(f'{api_base}/api/records', timeout=10)


@then('the response status should be 200')
def status_200(records_response):
    assert records_response.status_code == 200, records_response.text


@then('the response body should be a JSON array')
def is_json_array(records_response):
    data = records_response.json()
    assert isinstance(data, list), f'Expected list, got {type(data)}'


@given('a completed job record exists in DynamoDB', target_fixture='seeded_job_id')
def seed_record(job_state_table, context):
    """Seed a synthetic SUCCEEDED record directly into DynamoDB."""
    job_id = f'pytest-{uuid.uuid4()}'
    ddb = boto3.resource('dynamodb', region_name='us-east-1')
    table = ddb.Table(job_state_table)
    table.put_item(Item={
        'jobId': job_id,
        'status': 'SUCCEEDED',
        'extractedText': 'pytest synthetic record',
        'createdAt': '2026-01-01T00:00:00',
    })
    context['seeded_job_id'] = job_id
    return job_id


@when('I DELETE the record via "/api/records/{jobId}"', target_fixture='delete_response')
def delete_record(api_base, context):
    job_id = context['seeded_job_id']
    return requests.delete(f'{api_base}/api/records/{job_id}', timeout=10)


@then('the response status should be 204')
def status_204(delete_response):
    assert delete_response.status_code == 204, delete_response.text


@then('the record is no longer returned by GET /api/records')
def record_gone(api_base, context):
    job_id = context['seeded_job_id']
    resp = requests.get(f'{api_base}/api/records', timeout=10)
    assert resp.status_code == 200
    ids = [r['jobId'] for r in resp.json()]
    assert job_id not in ids, f'Record {job_id} still present after DELETE'
