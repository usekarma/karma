#!/usr/bin/env python3

import argparse
import boto3
import json
import os
import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile

lambda_client = boto3.client("lambda")
ssm = boto3.client("ssm")

def install_dependencies(lambda_dir, dist_dir):
    req_file = lambda_dir / "requirements.txt"
    if req_file.exists():
        print("📦 Installing dependencies from requirements.txt...")
        subprocess.run([
            "pip", "install",
            "--target", str(dist_dir),
            "-r", str(req_file),
            "--upgrade"
        ], check=True)

def build_lambda(nickname):
    lambda_dir = Path(f"lambdas/{nickname}").resolve()
    dist_dir = lambda_dir / "dist"
    dist_zip = dist_dir / f"{nickname}.zip"

    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True)

    # Copy .py files
    for file in lambda_dir.glob("*.py"):
        shutil.copy(file, dist_dir)

    # Install dependencies
    install_dependencies(lambda_dir, dist_dir)

    # Zip contents
    print(f"📦 Creating ZIP file: {dist_zip}")
    with ZipFile(dist_zip, "w") as zipf:
        for file in dist_dir.rglob("*"):
            zipf.write(file, arcname=file.relative_to(dist_dir))

    return dist_zip

def publish_lambda(nickname, zip_path):
    print(f"🚀 Publishing Lambda: {nickname}")
    with open(zip_path, "rb") as f:
        response = lambda_client.update_function_code(
            FunctionName=nickname,
            ZipFile=f.read(),
            Publish=True
        )
    return response["FunctionArn"]

def put_ssm_parameter(nickname, versioned_arn):
    unversioned_arn = ":".join(versioned_arn.split(":")[:7])  # remove version
    param_path = f"/iac/lambda/{nickname}/runtime"
    print(f"📝 Writing runtime ARN to SSM: {param_path}")
    ssm.put_parameter(
        Name=param_path,
        Value=json.dumps({"arn": unversioned_arn}),
        Type="String",
        Overwrite=True
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("nickname", help="Lambda nickname (directory name under lambdas/)")
    args = parser.parse_args()

    zip_path = build_lambda(args.nickname)
    versioned_arn = publish_lambda(args.nickname, zip_path)
    put_ssm_parameter(args.nickname, versioned_arn)

    print(f"✅ Lambda {args.nickname} deployed → {versioned_arn}")

if __name__ == "__main__":
    main()
