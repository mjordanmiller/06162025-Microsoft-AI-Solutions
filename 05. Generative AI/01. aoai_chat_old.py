from openai import AzureOpenAI
import os
import json
import datetime
from dotenv import load_dotenv


load_dotenv()

class OpenAIChatSession():
    """
    A class to manage a chat session with the Azure OpenAI service.

    This class provides methods to set up a chat session with the Azure OpenAI API, send messages,
    receive responses, and manage conversation history. It supports setting system messages,
    adding and clearing user messages, and saving the conversation history to a file.

    Attributes:
        endpoint (str): The endpoint for the Azure OpenAI API.
        api_key (str): The API key for accessing the Azure OpenAI service.
        api_version (str): The API version to use.
        client (AzureOpenAI): The Azure OpenAI client initialized with the API key, endpoint, and version.
        model (str): The model to use for the chat session. Default is 'skillstorm-gpt4o'.
        temperature (float): The temperature for the response. Default is 1.
        max_tokens (int): The maximum number of tokens for the response. Default is 1000.
        top_p (float): The top_p value for nucleus sampling. Default is 0.95.
        frequency_penalty (float): The frequency penalty for the response. Default is 0.
        presence_penalty (float): The presence penalty for the response. Default is 0.
        stop (list or None): The stop sequence(s) for the response. Default is None.
        system_message (str): The initial system message to set the context for the chat session.
        total_tokens (int): The total number of tokens used in the chat session.
        last_prompt (str): The last prompt sent to the API.
        last_response (str): The last response received from the API.
        messages (list): A list of messages exchanged in the chat session.

    Methods:
        set_system_message(message):
            Sets the system message for the chat session.

        add_message(message, role='user'):
            Adds a message to the conversation history.

        clear_messages():
            Clears all messages and resets the conversation history with the system message.

        chat(prompt):
            Sends a prompt to the Azure OpenAI API and processes the response.

        start():
            Starts an interactive chat session, allowing user input from the console.

        save():
            Saves the conversation history to a file in JSON format.
    """

    def __init__(self, model='skillstorm-gpt4o'):
        self.endpoint = os.environ['AOAI_ENDPOINT']
        self.api_key = os.environ['AOAI_KEY']
        self.api_version = '2024-02-01'

        self.client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            api_key=self.api_key
        )

        # Chat Settings
        self.model = model
        self.temperature = 1
        self.max_tokens = 1000 #response length
        self.top_p = 0.95
        self.frequency_penalty = 0
        self.presence_penalty = 0
        self.stop = None
        self.system_message = "You are an AI assistant that helps people learn. Responses should be consise and to the point."

        # Prompt Management Variables
        self.total_tokens = 0
        self.last_prompt = ""
        self.last_response = ""

        # Construct the initial messages
        self.messages = []
        self.add_message(message=self.system_message, role='system')

    def set_system_message(self, message):
        self.system_message = message
        self.messages[0] = {"role": "system", "content": message}

    def add_message(self, message, role='user'):
        self.messages.append({"role":role, "content": message})
    
    def clear_messages(self):
        self.messages = []
        self.add_message(role="system", message=self.system_message)

    def chat(self, prompt):
        self.add_message(message=prompt)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stop=self.stop
        )

        # Process response
        response_text = response.choices[0].message.content
        self.last_prompt = prompt
        self.last_response = response_text
        self.total_tokens += response.usage.total_tokens

        print(f"Azure OpenAI: {response_text}")
        self.add_message(role='assistant', message=response_text)

    def start(self):
        print(f"Starting a chat session with the {self.model} model. Type 'exit', 'quit', or 'stop' to end the session. \
                Type 'save' to write the conversation to a file.")
        self.clear_messages()
        while True:
            next_message = input("User: ")
            if next_message.strip().lower() in ['exit', 'quit', 'stop']:
                print("Exiting...")
                break
            if next_message.strip().lower() == 'save':
                self.save()
                print("Saving session...")
                continue
            self.chat(next_message)
        
    def save(self):
        path = os.path.dirname(__file__)
        base_path = os.path.split(path)[0]
        print(base_path)
        now = datetime.datetime.now()
        file_name = f"{now.strftime('%Y%m%d %H-%M-%S')} Session Messages.json"
        file_path = os.path.join(base_path + '\\data\\AzureOpenAI\\' + file_name)
        print(file_path)
        with open(file_path, 'w') as f:
            f.write(json.dumps(self.messages, indent=4))


if __name__ == "__main__":
    chat = OpenAIChatSession()
    chat.start()

