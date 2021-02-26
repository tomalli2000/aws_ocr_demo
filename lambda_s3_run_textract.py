import json
import boto3

class ProcessType:
    DETECTION = 1
    ANALYSIS = 2
    
class DocumentProcessor:
    jobId = ''
    textract = boto3.client('textract')
    
    roleArn = ''   
    bucket = ''
    document = ''
    
    snsTopicArn = ''
    processType = ''

    def __init__(self, role, bucket, document, snsArn):    
        self.roleArn = role
        self.bucket = bucket
        self.document = document   
        self.snsTopicArn = snsArn 

    def ProcessDocument(self,type):
        
        self.processType=type
        validType=False

        print( "Bucket: " + self.bucket )
        print( "Doc:    " + self.document )
        print( "Role:   " + self.roleArn )
        print( "SNS:    " + self.snsTopicArn )
        
        #Determine which type of processing to perform
        if self.processType==ProcessType.DETECTION:
            
            response = self.textract.start_document_text_detection(
                DocumentLocation={'S3Object': {'Bucket': self.bucket, 'Name': self.document}},
                NotificationChannel={'RoleArn': self.roleArn, 'SNSTopicArn': self.snsTopicArn}
                )
            print('Processing type: Detection')
            validType=True        

        
        if self.processType==ProcessType.ANALYSIS:
            response = self.textract.start_document_analysis(DocumentLocation={'S3Object': {'Bucket': self.bucket, 'Name': self.document}},
                FeatureTypes=["TABLES", "FORMS"],
                NotificationChannel={'RoleArn': self.roleArn, 'SNSTopicArn': self.snsTopicArn})
            print('Processing type: Analysis')
            validType=True    

        if validType==False:
            print("Invalid processing type. Choose Detection or Analysis.")
            return

        print('Start Job Id: ' + response['JobId'])

def lambda_handler(event, context):
    # TODO implement
    roleArn = 'arn:aws:iam::329520552698:role/TextractRole'   
    snsArn = "arn:aws:sns:us-east-1:329520552698:OCR_COMPLETE"
    iFilesProcessed = 0
 
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        document = record['s3']['object']['key']
        
        analyzer=DocumentProcessor(roleArn, bucket, document,snsArn)
        analyzer.ProcessDocument(ProcessType.DETECTION)  
        iFilesProcessed += 1
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Processed {iFilesProcessed} files.')
    }
