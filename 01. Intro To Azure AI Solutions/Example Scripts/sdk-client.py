'''
NOTE: THIS FILE DOES NOT FOLLOW BEST PRACTICES and is meant to give you an understanding of how to interact with the REST APIs

You should never save your endpoint or key in plain text
'''


#Import necessary libraries/modules
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

def main():
    global ai_endpoint
    global ai_key

    try:
        # Get Configuration Settings
        ai_endpoint = 'AI_SERVICE_ENDPOINT'
        ai_key = 'AI_SERVICE_KEY'

        # Get user input (until they enter "quit")
        userText =''
        while userText.lower() != 'quit':
            userText = input('\nEnter some text ("quit" to stop)\n')
            if userText.lower() != 'quit':
                language = GetLanguage(userText)
                print('Language:', language)

    except Exception as ex:
        print(ex)


#This function (when called) makes a request to the Language API 
def GetLanguage(text):

    # Create client using endpoint and key
    # A client is the object used to make API calls
    credential = AzureKeyCredential(ai_key)
    client = TextAnalyticsClient(endpoint=ai_endpoint, credential=credential)

    
    # Call the service to get the detected language
    detectedLanguage = client.detect_language(documents = [text])[0]
    return detectedLanguage.primary_language.name


if __name__ == "__main__":
    main()