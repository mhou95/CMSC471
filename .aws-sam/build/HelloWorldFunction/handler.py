import json

def handler(event, context):
    # Log the event argument for debugging and for use in local development.
    print(json.dumps(event))

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": "Hello World"
        })
    }