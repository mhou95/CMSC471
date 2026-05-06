"""Acceptance tests: upload image to /api/inbox (Story S5)."""
import base64
import io
import json

import pytest
import requests
from pytest_bdd import given, scenarios, then, when

scenarios('features/upload_image.feature')

# Minimal 1x1 white JPEG (69 bytes — no external file needed)
_TINY_JPEG_B64 = (
    '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkS'
    'Ew8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAAR'
    'CAABAAEDASIAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAA'
    'AAAAAAAAAAAAAP/EABQBAQAAAAAAAAAAAAAAAAAAAAD/xAAUEQEAAAAAAAAAAAAA'
    'AAAAAAAA/9oADAMBAAIRAxEAPwCwABmX/9k='
)
_TINY_JPEG = base64.b64decode(_TINY_JPEG_B64)


@given('the API is deployed', target_fixture='api_base')
def api_deployed(api_endpoint):
    return api_endpoint


@when('I POST a small test image to "/api/inbox"', target_fixture='upload_response')
def post_image(api_base, context):
    payload = {'filename': 'pytest-tiny.jpg', 'data': _TINY_JPEG_B64}
    r = requests.post(f'{api_base}/api/inbox', json=payload, timeout=15)
    context['upload_response'] = r
    context['object_key'] = r.json().get('objectKey') if r.ok else None
    return r


@then('the response status should be 200')
def status_200(upload_response):
    assert upload_response.status_code == 200, upload_response.text


@then('the response body should contain an "objectKey"')
def has_object_key(upload_response):
    data = upload_response.json()
    assert 'objectKey' in data, f'Missing objectKey in {data}'


@when('I GET "/api/inbox"', target_fixture='list_response')
def get_inbox(api_base):
    return requests.get(f'{api_base}/api/inbox', timeout=10)


@then('the response status should be 200', target_fixture=None)
def list_status_200(list_response):
    assert list_response.status_code == 200, list_response.text


@then('the response body should contain a "files" list')
def has_files_list(list_response):
    data = list_response.json()
    assert 'files' in data and isinstance(data['files'], list)


@given('a file has been uploaded to the inbox', target_fixture='uploaded_key')
def upload_file_for_delete(api_base, context):
    payload = {'filename': 'pytest-delete-me.jpg', 'data': _TINY_JPEG_B64}
    r = requests.post(f'{api_base}/api/inbox', json=payload, timeout=15)
    assert r.status_code == 200, r.text
    key = r.json()['objectKey']
    context['uploaded_key'] = key
    return key


@when('I DELETE the uploaded file from "/api/inbox/{key}"', target_fixture='delete_response')
def delete_file(api_base, context):
    key = context['uploaded_key']
    return requests.delete(f'{api_base}/api/inbox/{key}', timeout=10)


@then('the response status should be 204')
def status_204(delete_response):
    assert delete_response.status_code == 204, delete_response.text
