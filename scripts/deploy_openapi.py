#!/usr/bin/env python3

import argparse
import boto3
import json
from pathlib import Path
from urllib.parse import urlparse

ssm = boto3.client("ssm")
s3 = boto3.client("s3")


def get_ssm_parameter(name):
    response = ssm.get_parameter(Name=name)
    return json.loads(response["Parameter"]["Value"])


def put_ssm_parameter(name, value):
    ssm.put_parameter(
        Name=name,
        Value=json.dumps(value),
        Type="String",
        Overwrite=True,
        Tier="Standard"
    )


def upload_openapi(bucket, key, local_path):
    print(f"📤 Uploading {local_path} to s3://{bucket}/{key}")
    s3.upload_file(str(local_path), bucket, key)


def main():
    parser = argparse.ArgumentParser(description="Deploy an OpenAPI spec to S3 and update the runtime pointer.")
    parser.add_argument("openapi_nickname", help="OpenAPI nickname (e.g. karma-api)")
    parser.add_argument("--bucket-nickname", help="S3 bucket nickname (default: same as OpenAPI nickname)")
    parser.add_argument("--file", help="Path to openapi.yaml (default: openapi/<nickname>/openapi.yaml)")
    parser.add_argument("--region", default="us-east-1")

    args = parser.parse_args()

    openapi_nickname = args.openapi_nickname
    bucket_nickname = args.bucket_nickname or openapi_nickname
    openapi_file = Path(args.file or f"openapi/{openapi_nickname}/openapi.yaml")

    if not openapi_file.exists():
        raise FileNotFoundError(f"❌ OpenAPI file not found: {openapi_file}")

    # Step 1: Get bucket from runtime param
    bucket_param_path = f"/iac/s3-bucket/{bucket_nickname}/runtime"
    bucket_data = get_ssm_parameter(bucket_param_path)
    bucket_name = bucket_data["bucket_name"]

    key = openapi_file.name  # e.g. karma-api.yaml
    upload_openapi(bucket_name, key, openapi_file)

    # Step 2: Write runtime param
    runtime_param_path = f"/iac/openapi/{openapi_nickname}/runtime"
    openapi_ref = f"s3://{bucket_name}/{key}"
    put_ssm_parameter(runtime_param_path, {"source": openapi_ref})

    print(f"✅ Published OpenAPI to {runtime_param_path}")
    print(f"   → {openapi_ref}")


if __name__ == "__main__":
    main()
