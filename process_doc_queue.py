import boto3
import json

class DocQueueProcessor:
    textract = boto3.client('textract')
    sqs = boto3.client('sqs')
    sqsQueueUrl = ''

    def __init__(self, sqsName):    
        self.sqsQueueUrl = self.sqs.get_queue_url(QueueName=sqsName)['QueueUrl']    

    def process_queue(self):

        sqsResponse = self.sqs.receive_message(QueueUrl=self.sqsQueueUrl, 
                                          MessageAttributeNames=['ALL'],
                                          MaxNumberOfMessages=10)

        if sqsResponse:     
            if 'Messages' not in sqsResponse:
                sqsResponse['Messages'] = []
    
            for message in sqsResponse['Messages']:
                notification = json.loads(message['Body'])
                textMessage = json.loads(notification['Message'])
                print(textMessage['Status'])
                if (textMessage['Status'] == "SUCCEEDED"):
                    print("Job:    " + textMessage['JobId'])
                    print("Bucket: " + textMessage['DocumentLocation']['S3Bucket'])
                    print("Object: " + textMessage['DocumentLocation']['S3ObjectName'])
                    self.GetResults(textMessage['JobId'],textMessage['DocumentLocation'])
                    self.sqs.delete_message(QueueUrl=self.sqsQueueUrl,
                                    ReceiptHandle=message['ReceiptHandle'])

    def GetResults(self, jobId, docInfo):
        maxResults = 1000
        paginationToken = None
        finished = False
        response=None
        response_page=None

        while (not finished):
            if paginationToken==None:
                response = self.textract.get_document_text_detection(JobId=jobId,
                    MaxResults=maxResults)
                if 'NextToken' in response:
                    paginationToken = response['NextToken']
                else:
                    finished = True           
            else: 
                response_page = self.textract.get_document_text_detection(JobId=jobId,
                    MaxResults=maxResults,
                    NextToken=paginationToken)     

                response['Blocks'] += response_page['Blocks']   

                if 'NextToken' in response_page:
                    paginationToken = response_page['NextToken']
                else:
                    finished = True   

        if finished:
            response['DocumentLocation'] = docInfo
            result_summary = self.findUnityNumber(response)
            resultfile = jobId + ".results.json"
            print (f"Saving Job to {resultfile}")
            with open(resultfile, 'w') as fp:
                json.dump(result_summary, fp)

    def findUnityNumber(self, responseDict):
        
        resultFound = []

        for block in responseDict["Blocks"]: 
            if "Text" in block.keys() and \
               "UNITY" in block["Text"].upper() and \
               block["BlockType"] == "LINE":
                print()
                print("Bucket:     " + responseDict['DocumentLocation']['S3Bucket'])
                print("Object:     " + responseDict['DocumentLocation']['S3ObjectName'])
                print("Page      : " + str(block["Page"]))
                print("Unity Line: " + block["Text"])
                print("Confidence: " + str(block["Confidence"]))

                detection = {
                    "Bucket": responseDict['DocumentLocation']['S3Bucket'],
                    "Object": responseDict['DocumentLocation']['S3ObjectName'],
                    "Page": block["Page"],
                    "Unity": block["Text"],
                    "Confidence": block["Confidence"] }

                resultFound.append(detection)
        return resultFound            
    
def main():
    sqsName = "OCR_COMPLETE_Q"
    analyzer=DocQueueProcessor(sqsName)
    analyzer.process_queue()    


if __name__ == "__main__":
    main() 