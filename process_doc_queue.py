import boto3
import json
import logging as log

class DocQueueProcessor:
    textract = boto3.client('textract')
    sqs = boto3.client('sqs')
    sqsQueueUrl = ''

    def __init__(self, sqsName):    
        self.sqsQueueUrl = self.sqs.get_queue_url(QueueName=sqsName)['QueueUrl']    

    def get_results_from_sqs_message(self, message_body):
        
        result_summary = None
        notification = json.loads(message_body)
        textMessage = json.loads(notification['Message'])
        if (textMessage['Status'] == "SUCCEEDED"):
            log.info("Job:" + textMessage['JobId'])
            log.info("Bucket:" + textMessage['DocumentLocation']['S3Bucket'])
            log.info("Object:" + textMessage['DocumentLocation']['S3ObjectName'])
            result_summary = self.GetResults(textMessage['JobId'],textMessage['DocumentLocation'])
        return result_summary

    
    def process_one_sqs_message(self):

        result_summary = None
        sqsResponse = self.sqs.receive_message(QueueUrl=self.sqsQueueUrl, 
                                          MessageAttributeNames=['ALL'],
                                          MaxNumberOfMessages=1)

        if sqsResponse:     
            if 'Messages' in sqsResponse:
                message = sqsResponse['Messages'][0]
                result_summary = self.get_results_from_sqs_message(message['Body'])
                self.sqs.delete_message(QueueUrl=self.sqsQueueUrl,
                                    ReceiptHandle=message['ReceiptHandle'])
        return result_summary
    
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
            response['unity'] = self.findUnityNumberInTextract(response)

        with open(response['DocumentLocation']['S3ObjectName'].replace('/','_').replace(' ','_') + '.json', 'w') as fp:
            json.dump(response, fp)

        return response['unity']

    def findUnityInLine(self, line):

        if "UNITY" in line.upper() or "BATCH" in line.upper():
            for w in line.split():
                unity_num = ''.join(letter for letter in w if letter in '0123456789')
                if len(unity_num) == len(w) and len(unity_num) >= 5:
                    return unity_num
        return "" 


    def findUnityNumberInTextract(self, responseDict):
        
        unity_scan_results = {}
        unity_scan_results['DocumentLocation'] = responseDict['DocumentLocation']
        unity_scan_results["ScanResults"] = []
        
        for block in responseDict["Blocks"]: 
            if "Text" in block.keys() and block["BlockType"] == "LINE":
                unity_num = self.findUnityInLine(block["Text"])
                if len(unity_num) >= 5:
                    detection = {
                        "Page": block["Page"],
                        "Unity Line": block["Text"],
                        "Unity": unity_num,
                        "Confidence": block["Confidence"] }
                    unity_scan_results["ScanResults"].append(detection)
        return unity_scan_results            
    
    def detect_in_json_file(self, filename):
        
        with open(filename) as json_file:
            response = json.load(json_file)
            response['unity'] = self.findUnityNumberInTextract(response)
        return response['unity']


def main():
    
    analyzer=DocQueueProcessor('OCR_COMPLETE_Q')
    print(analyzer.process_one_sqs_message())    

    #print(analyzer.detect_in_json_file("input_07-27-2018_Accounts_Payable_06-01-2018_to_06-14-2018.pdf.json"))


if __name__ == "__main__":
    main() 