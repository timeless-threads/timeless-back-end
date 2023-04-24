import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

likes_table_name = 'revive_user_likes'
item_table_name = 'used_clothing_database'
dynamodb = boto3.resource('dynamodb')

# Partition key: user_id (string)
# Sort key: item_uuid (string)
likes_table = dynamodb.Table(likes_table_name)
items_table = dynamodb.Table(item_table_name)

get_method = 'GET'
post_method = 'POST'
delete_method = 'DELETE'

def lambda_handler(event, context):
    logger.info('Received event: ' + json.dumps(event))
    method = event['httpMethod']
    if method == get_method:
        return get(event)
    elif method == post_method:
        return post(event)
    elif method == delete_method:
        return delete(event)
    else:
        return buildResponse(404, {'message': 'Method not supported'})

def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*', # Allow CORS
        }
    }

    if body is not None:
        response['body'] = json.dumps(body)
    
    return response

def get(event):
    user_id = event['queryStringParameters']['user_id']
    response = likes_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
    )

    returned_items = []
    for item in response['Items']:
        try:
            item['item_uuid'] = item['item_uuid']

            # Make a query using to used_clothing_database using the item_uuid and global secondary index uuid-index
            items_table_response = items_table.query(
                IndexName='uuid-index',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('uuid').eq(item['item_uuid'])
            )

            # Get the first item from the response
            item.update(items_table_response['Items'][0])

            # Add the item details to the response
            returned_items.append(item)
        except:
            pass


    return buildResponse(200, returned_items)

def post(event):
    body = json.loads(event['body'])
    user_id = body['user_id']
    item_uuid = body['item_uuid']
    response = likes_table.put_item(
        Item={
            'user_id': user_id,
            'item_uuid': item_uuid
        }
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return buildResponse(200, {'message': 'Item added'})
    else:
        return buildResponse(500, {'message': 'Item not added'})

def delete(event):
    body = json.loads(event['body'])
    user_id = body['user_id']
    item_uuid = body['item_uuid']
    response = likes_table.delete_item(
        Key={
            'user_id': user_id,
            'item_uuid': item_uuid
        }
    )

    # Check if item was deleted
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return buildResponse(200, {'message': 'Item deleted'})
    else:
        return buildResponse(500, {'message': 'Item not found'})