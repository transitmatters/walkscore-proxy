import boto3
import json
import time


class DynamoDBCache:
    def __init__(self, table_name="walkscore-cache", ttl_seconds=86400):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)
        self.ttl_seconds = ttl_seconds

    def get(self, key):
        try:
            response = self.table.get_item(Key={"cache_key": key})
            if "Item" in response:
                item = response["Item"]
                # Check if item has expired
                if time.time() < item["expires_at"]:
                    return json.loads(item["data"])
                else:
                    # Item expired, delete it
                    self.delete(key)
            return None
        except Exception as e:
            print(f"Error getting cache item: {e}")
            return None

    def set(self, key, data):
        try:
            expires_at = int(time.time()) + self.ttl_seconds
            self.table.put_item(
                Item={
                    "cache_key": key,
                    "data": json.dumps(data, default=str),
                    "expires_at": expires_at,
                    "ttl": expires_at,  # DynamoDB TTL attribute
                }
            )
        except Exception as e:
            print(f"Error setting cache item: {e}")

    def delete(self, key):
        try:
            self.table.delete_item(Key={"cache_key": key})
        except Exception as e:
            print(f"Error deleting cache item: {e}")
