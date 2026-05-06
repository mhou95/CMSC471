"""Acceptance tests: submit OCR job via /api/jobs (Story S6)."""
import base64
import json

import pytest
import requests
from pytest_bdd import given, scenarios, then, when

scenarios('features/submit_job.feature')

_TINY_JPEG_B64 = (
    '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkS'
    'Ew8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAAR'
    'CAABAAEDASIAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAA'
    'AAAAAAAAAAAAAP/EABQBAQAAAAAAAAAAAAAAAAAAAAD/xAAUEQEAAAAAAAAAAAAA'
    'AAAAAAAA/9oADAMBAAIRAxEAPwCwABmX/9k='
)


@given('the API is deployed', target_fixture='api_base')
def api_deployed(api_endpoint):
    return api_endpoint


@given('an image exists in the inbox bucket', target_fixture='image_key')
def upload_image(api_base):
    r = requests.post(
        f'{api_base}/api/inbox',
        json={'filename': 'pytest-ocr.jpg', 'data': _TINY_JPEG_B64},
        timeout=15,
    )
    assert r.status_code == 200, r.text
    return r.json()['objectKey']


@when('I POST the imageKey to "/api/jobs"', target_fixture='submit_response')
def post_job(api_base, image_key, context):
    r = requests.post(
        f'{api_base}/api/jobs',
        json={'imageKey': image_key},
        timeout=15,
    )
    context['submit_response'] = r
    if r.ok:
        context['job_id'] = r.json().get('jobId')
    return r


@then('the response status should be 200')
def status_200(submit_response):
    assert submit_response.status_code == 200, submit_response.text


@then('the response body should contain a "jobId"')
def has_job_id(submit_response):
    assert 'jobId' in submit_response.json()


@then('the response body should contain an "executionArn"')
def has_execution_arn(submit_response):
    assert 'executionArn' in submit_response.json()


@when('I POST an empty body to "/api/jobs"', target_fixture='bad_submit_response')
def post_empty_job(api_base):
    return requests.post(f'{api_base}/api/jobs', json={}, timeout=10)


@then('the response status should be 400')
def status_400(bad_submit_response):
    assert bad_submit_response.status_code == 400, bad_submit_response.text


@given('a job has been submitted', target_fixture='submitted_job_id')
def submit_job_for_poll(api_base, context):
    upload = requests.post(
        f'{api_base}/api/inbox',
        json={'filename': 'pytest-poll.jpg', 'data': _TINY_JPEG_B64},
        timeout=15,
    )
    assert upload.status_code == 200
    key = upload.json()['objectKey']
    r = requests.post(f'{api_base}/api/jobs', json={'imageKey': key}, timeout=15)
    assert r.status_code == 200
    job_id = r.json()['jobId']
    context['poll_job_id'] = job_id
    return job_id


@when('I GET "/api/jobs/{jobId}"', target_fixture='poll_response')
def poll_job(api_base, context):
    job_id = context['poll_job_id']
    return requests.get(f'{api_base}/api/jobs/{job_id}', timeout=10)


@then('the response status should be 200', target_fixture=None)
def poll_status_200(poll_response):
    assert poll_response.status_code == 200, poll_response.text


@then('the response body should contain a "status" field')
def has_status_field(poll_response):
    assert 'status' in poll_response.json()
