# Karma

Karma is a minimal infrastructure event graph powered by AWS Lambda and API Gateway. It supports logging infrastructure events and querying them as a graph, with all configuration resolved via nicknames and AWS Parameter Store.

---

## Features

- Logs structured infrastructure events to enable traceability  
- Provides a queryable graph API over logged events  
- Uses nicknamed Lambda functions and dynamic OpenAPI resolution  
- Deploys with simple Python scripts and no Terraform required

---

## Directory Structure

```
karma/
├── openapi/
│   └── karma-api/
│       └── openapi.yaml
│
├── lambdas/
│   ├── karma-log-handler/
│   │   ├── main.py
│   │   └── requirements.txt (optional)
│   └── karma-graph-query/
│       ├── main.py
│       └── requirements.txt (optional)
│
└── scripts/
    ├── deploy_lambda.py
    └── deploy_openapi.py
```

---

## OpenAPI Extensions

Each path operation in the OpenAPI spec uses the custom extension `x-lambda-nickname` to declare which Lambda should handle the request:

```yaml
paths:
  /events:
    post:
      summary: Log an event
      x-lambda-nickname: karma-log-handler
```

At deployment time, this nickname is resolved into a versioned ARN by querying Parameter Store:

```
/iac/lambda/karma-log-handler/runtime
```

This decouples the OpenAPI spec from any specific Lambda ARN, supporting dynamic resolution per environment.

---

## Deployment

### Lambda Deployment

```bash
python scripts/deploy_lambda.py karma-log-handler
```

- Zips the Lambda code
- Uploads it to AWS Lambda
- Publishes a new version
- Writes the versioned ARN to SSM: `/iac/lambda/<nickname>/runtime`

### API Deployment

```bash
python scripts/deploy_openapi.py karma-api
```

- Uploads the OpenAPI spec to an S3 bucket
- Records its location in Parameter Store: `/iac/openapi/<nickname>/runtime`

---

## Requirements

- Python 3.10+
- AWS CLI credentials (via `AWS_PROFILE`)
- `boto3`, `PyYAML` (install via `pip install -r requirements.txt`)
