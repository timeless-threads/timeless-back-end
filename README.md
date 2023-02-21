# revive-back-end

## File Structure
* `ddb-to-opensearch`: contains the code for the lambda function to stream from database to opensearch.

## Instructions
### ddb-to-opensearch
To deploy lambda
'''
# Install dependencies
pip install --target ./package requests
pip install --target ./package requests_aws4auth

# Zip for deployment
cd package
zip -r ../lambda.zip .
zip -g lambda.zip sample.py
'''