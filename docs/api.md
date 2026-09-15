# API Reference

Base URL after deployment:

```text
https://<api-id>.execute-api.<region>.amazonaws.com
```

## Create asset

`POST /assets`

```json
{
  "name": "Production-Web-01",
  "type": "EC2 Instance",
  "environment": "Production",
  "region": "us-east-2",
  "owner": "Cloud Operations",
  "status": "Active"
}
```

Returns HTTP `201` and the newly created asset, including its generated UUID and timestamps.

## List assets

`GET /assets`

Returns HTTP `200` with an array of asset records.

## Get asset

`GET /assets/{assetId}`

Returns HTTP `200` with the asset or HTTP `404` if it does not exist.

## Update asset

`PUT /assets/{assetId}`

Send the same six required asset fields used by the create operation. Returns HTTP `200` with the updated record or HTTP `404` if the asset does not exist.

## Delete asset

`DELETE /assets/{assetId}`

Returns HTTP `200` after deletion or HTTP `404` if the asset does not exist.

## Validation

The API requires `name`, `type`, `environment`, `region`, `owner`, and `status`. Invalid JSON returns HTTP `400`. Missing required fields return HTTP `400` with the missing field names.
