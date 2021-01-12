# Demo of AWS Textract Service

## Pre-Requisites
* Python 3.7+
* AWS Account
* For Local development only:
  * AWS CLI https://aws.amazon.com/cli/
  * Python SDK: boto3  https://aws.amazon.com/sdk-for-python/

## AWS Account & Code Setup
* IAM: Create a user named "ocr"
  * Make sure to capture the key and secret
  * Attach the following policies (or restricted equivilents):
    * AmazonSQSFullAccess
    * AmazonTextractFullAccess
    * AmazonS3ReadOnlyAccess
    * AmazonSNSFullAccess  
* IAM: Create a role named "TextractRole"
  * Attach the following policies (or restricted equivilents):
    * AmazonSQSFullAccess
    * AmazonTextractFullAccess
    * AmazonS3ReadOnlyAccess
    * AmazonSNSFullAccess 
  * Note the ARN of the role and update ocr_submit.py:62
* SNS: Create an SNS topic named OCR_COMPLETE
  * Note the ARN of the SNS topic and update ocr_submit.py:67
* SQS: Create a SQS queue named OCR_COMPLETE_Q
    * Subscribe the SQS queue OCR_COMPLETE_Q to SNS topic OCR_COMPLETE
* S3: Create a bucket in us-east-1 and upload the files
  * Note the bucket and file name, and update ocr_submit.py:63 and line 66

## Configuring your local host
* Run aws configure --profile ocr
  * Set the key and secret for the "ocr" user
  * Set the region to us-east-1

## Running the code
* Run ocr_submit.py
  * Wait for processing Completion
  * Optionally, subscribe your email address to the SNS topic OCR_COMPLETE to get an email
* Run process_doc_queue.py

## Thoughts on using Lambda to run serverless
* Convert ocr_submit.py to a Lamba function that runs when an object is added to S3.
* Convert process_doc_queue.py to one of the below:
  * Lambda triggered by SQS
  * -or- remove the SQS queue, and have a lamdba triggered on SNS

