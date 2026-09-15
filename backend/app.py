import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLE_NAME", "CloudOpsAssets")
table = boto3.resource("dynamodb").Table(TABLE_NAME)


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        },
        "body": json.dumps(body),
    }


def now():
    return datetime.now(timezone.utc).isoformat()


def parse_body(event):
    try:
        return json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return None


def validate_asset(data):
    required = ["name", "type", "environment", "region", "owner", "status"]
    missing = [field for field in required if not str(data.get(field, "")).strip()]
    return missing


def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method") or event.get("httpMethod")
    path_params = event.get("pathParameters") or {}
    asset_id = path_params.get("assetId")

    if method == "OPTIONS":
        return response(204, {})

    try:
        if method == "GET" and not asset_id:
            result = table.scan()
            return response(200, result.get("Items", []))

        if method == "GET" and asset_id:
            result = table.get_item(Key={"assetId": asset_id})
            item = result.get("Item")
            return response(200, item) if item else response(404, {"message": "Asset not found"})

        if method == "POST":
            data = parse_body(event)
            if data is None:
                return response(400, {"message": "Invalid JSON"})
            missing = validate_asset(data)
            if missing:
                return response(400, {"message": "Missing required fields", "fields": missing})
            timestamp = now()
            item = {
                "assetId": str(uuid.uuid4()),
                "name": data["name"].strip(),
                "type": data["type"].strip(),
                "environment": data["environment"].strip(),
                "region": data["region"].strip(),
                "owner": data["owner"].strip(),
                "status": data["status"].strip(),
                "createdAt": timestamp,
                "updatedAt": timestamp,
            }
            table.put_item(Item=item)
            return response(201, item)

        if method == "PUT" and asset_id:
            data = parse_body(event)
            if data is None:
                return response(400, {"message": "Invalid JSON"})
            missing = validate_asset(data)
            if missing:
                return response(400, {"message": "Missing required fields", "fields": missing})
            existing = table.get_item(Key={"assetId": asset_id}).get("Item")
            if not existing:
                return response(404, {"message": "Asset not found"})
            item = {
                **existing,
                "name": data["name"].strip(),
                "type": data["type"].strip(),
                "environment": data["environment"].strip(),
                "region": data["region"].strip(),
                "owner": data["owner"].strip(),
                "status": data["status"].strip(),
                "updatedAt": now(),
            }
            table.put_item(Item=item)
            return response(200, item)

        if method == "DELETE" and asset_id:
            table.delete_item(
                Key={"assetId": asset_id},
                ConditionExpression="attribute_exists(assetId)",
            )
            return response(200, {"message": "Asset deleted", "assetId": asset_id})

        return response(405, {"message": "Method not allowed"})

    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return response(404, {"message": "Asset not found"})
        print(exc)
        return response(500, {"message": "Database operation failed"})
    except Exception as exc:
        print(exc)
        return response(500, {"message": "Internal server error"})
