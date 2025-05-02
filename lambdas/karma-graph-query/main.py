import json

def handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        query_type = body.get("query_type")
        parameters = body.get("parameters", {})

        if not query_type:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'query_type'"})
            }

        # Mock response based on query_type
        if query_type == "recent_changes":
            result = {
                "nodes": [
                    {"id": "node1", "label": "LambdaUpdate"},
                    {"id": "node2", "label": "SSMChange"}
                ],
                "edges": [
                    {"from": "node1", "to": "node2", "label": "triggers"}
                ]
            }
        elif query_type == "dependencies":
            result = {
                "nodes": [
                    {"id": "vpc", "label": "VPC"},
                    {"id": "subnet", "label": "Subnet"}
                ],
                "edges": [
                    {"from": "vpc", "to": "subnet", "label": "contains"}
                ]
            }
        else:
            result = {"nodes": [], "edges": []}

        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
