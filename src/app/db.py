import boto3
import os
from datetime import datetime, timezone

DYNAMO_TABLE = os.getenv('DYNAMO_TABLE')

# def get_item(id):
#     dynamodb = boto3.resource(
#         'dynamodb',
#         region_name='us-east-1',
#     )
#     try:
#         table = dynamodb.Table(DYNAMO_TABLE) 
#         response = table.get_item(Key={"userID": id})
#         item = response.get("Item")
#         return item["Query"]
#     except Exception:
#         return -1
    
def get_all_items(id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(DYNAMO_TABLE)
    
    try:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('userID').eq(id)
        )
        items = response.get('Items', [])
        return items
    except Exception as e:
        print(f"Error querying items: {e}")
        return []


def add_item(id, value):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table(DYNAMO_TABLE)

    timestamp = datetime.now(timezone.utc).isoformat()

    response = table.put_item(
        Item={
            'userID': id,
            'timestamp' : timestamp,
            'UserMessages': value,
        }
    )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("Item added successfully!")
    else:
        print("Error adding item.")