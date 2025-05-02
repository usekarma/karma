import json
import os
import boto3

def handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    
    # TODO: Insert into Karma graph (this is just stubbed for now)
    
    return {
        "statusCode": 201,
        "body": json.dumps({"message": "Event logged successfully"})
    }
