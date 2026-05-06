import boto3
import pytest

STACK_NAME = 'cmsc471-final'


@pytest.fixture(scope='session')
def stack_outputs():
    cfn = boto3.client('cloudformation', region_name='us-east-1')
    resp = cfn.describe_stacks(StackName=STACK_NAME)
    outputs = resp['Stacks'][0].get('Outputs', [])
    return {o['OutputKey']: o['OutputValue'] for o in outputs}


@pytest.fixture(scope='session')
def api_endpoint(stack_outputs):
    url = stack_outputs.get('ApiEndpoint', '')
    assert url, 'ApiEndpoint not found in stack outputs — is the stack deployed?'
    return url.rstrip('/')


@pytest.fixture(scope='session')
def inbox_bucket(stack_outputs):
    return stack_outputs['InboxBucketName']


@pytest.fixture(scope='session')
def job_state_table(stack_outputs):
    return stack_outputs['JobStateTableName']


# Shared mutable context dict injected into each BDD scenario
@pytest.fixture
def context():
    return {}
