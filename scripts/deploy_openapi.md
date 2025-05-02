# deploy_openapi.py

This script publishes an OpenAPI spec to S3 and updates the corresponding runtime pointer in AWS Systems Manager (SSM). It is the standard way to deploy the Karma API definition for use with infrastructure components such as `serverless-rest`.

---

## What It Does

- Uploads `openapi/<nickname>/openapi.yaml` to an S3 bucket
- Looks up the bucket name using:
  ```
  /iac/s3-bucket/<bucket-nickname>/runtime
  ```
- Writes a runtime pointer to:
  ```
  /iac/openapi/<nickname>/runtime
  ```

This pointer is used by the API Gateway deployment process to locate the OpenAPI spec.

---

## Usage

From the root of the `karma` repository:

```bash
python scripts/deploy_openapi.py karma-api
```

This will:

1. Upload `openapi/karma-api/openapi.yaml`
2. Write the following SSM parameter:
   ```
   /iac/openapi/karma-api/runtime
   ```
   with contents like:
   ```json
   {
     "openapi_ref": "s3://usekarma.dev-prod-karma-api/karma-api.yaml"
   }
   ```

---

## Git-Based Behavior

This script deploys the spec currently checked out in your Git branch. There is no version tagging or branching logic — what you have locally is what gets published.

---

## Optional Arguments

```bash
python scripts/deploy_openapi.py karma-api \
  --bucket-nickname openapi-storage \
  --file path/to/alt-openapi.yaml
```

- `--bucket-nickname`: overrides the default S3 bucket nickname (defaults to `karma-api`)
- `--file`: deploys a specific OpenAPI file (defaults to `openapi/<nickname>/openapi.yaml`)

---

## Requirements

Before running this script:

- The S3 bucket must already exist and be deployed via the `s3-bucket` component
- The OpenAPI file must include `x-lambda-nickname` values
- Each nickname must be resolvable via:
  ```
  /iac/lambda/<nickname>/runtime
  ```

---

## Integration

After publishing, the `serverless-rest` component can be deployed using:

```bash
AWS_PROFILE=prod ./scripts/deploy.sh serverless-rest karma-api
```

It will:

- Read the OpenAPI pointer from `/iac/openapi/karma-api/runtime`
- Resolve Lambda nicknames from SSM
- Deploy a functional API Gateway configuration

---

## Related Files

- `openapi/karma-api/openapi.yaml`: the source API definition
- `scripts/deploy_openapi.py`: this deployment script
- `serverless-rest`: the consuming infrastructure component (in `aws-iac`)
