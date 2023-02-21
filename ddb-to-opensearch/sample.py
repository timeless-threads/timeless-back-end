import boto3
import requests
from requests_aws4auth import AWS4Auth

region = 'us-east-1' # e.g. us-east-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://search-revive-2-rv74fa5b4ntji6jf6zi64voj6i.us-east-1.es.amazonaws.com' # the OpenSearch Service domain, e.g. https://search-mydomain.us-west-1.es.amazonaws.com
index = 'used_clothing_database'
datatype = '_doc'
url = host + '/' + index + '/' + datatype + '/'

headers = { "Content-Type": "application/json" }

def handler(event, context):
    count = 0
    for record in event['Records']:
        # Get the primary key for use as the OpenSearch ID
        id = record['dynamodb']['Keys']['product_name']['S']

        if record['eventName'] == 'REMOVE':
            r = requests.delete(url + id, auth=awsauth)
        else:
            document = record['dynamodb']['NewImage']
            r = requests.put(url + id, auth=awsauth, json=document, headers=headers)
        
        # Check status
        if r.status_code // 100 != 2:
            print(r.status_code)
            print(r.text)
            raise Exception("Error indexing document")
        count += 1

    return str(count) + ' records processed.'