# Request Asynchronous processing of text in a document stored in an S3 bucket. 
# For set up information, see https://docs.aws.amazon.com/textract/latest/dg/async.html

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

def main():
    roleArn = 'arn:aws:iam::329520552698:role/TextractRole'   
    bucket = 'tr-ocr-test-2020'
    # document = 'samplepacket.pdf'
    # document = 'Scan2.pdf'
    document = "samplecover-neo.png"
    snsArn = "arn:aws:sns:us-east-1:329520552698:OCR_COMPLETE"
    
    analyzer=DocumentProcessor(roleArn, bucket, document,snsArn)
    analyzer.ProcessDocument(ProcessType.DETECTION)


if __name__ == "__main__":
    main() 