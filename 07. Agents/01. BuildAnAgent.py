'''
In this script, we'll use Azure AI Agent Service to create a simple agent
that analyzes data and creates charts. The agent can use the built-in Code Interpreter tool to dynamically generate any code required to analyze data.

- Review the code to see how the agent is created and how it interacts with the user
- login to Azure using the Azure CLI
- set up a .env file with your Azure AI Foundry Project endpoint and model deployment name
- run the script and enter the following prompts:
    - What's the category with the highest cost?
    - Create a text-based bar chart showing cost by category
    - What's the standard deviation of cost?
 The thread is stateful, so it retains the conversation history - meaning that the agent has the full context for each response.
 Enter quit when you’re done.
'''
'''
NOTE:
This demo uses the user's Azure login credentials rather than passing API keys directly in the code.

You install the Azure CLI and sign in from your local development environment, so that you can use your user credentials to call Azure OpenAI in Azure AI Foundry Models.

Install the CLI in your terminal with the following command:
```PowerShell
winget install -e --id Microsoft.AzureCLI
```
In linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

In Mac: brew update && brew install azure-cli

After you install the Azure CLI, sign in using the `az login` command and sign-in using the browser

*If az login does not work in your terminal, and you get something like `The term 'az' is not recognized...`, even though the Azure CLI is installed, its executable is not in your system's PATH environment variable, so PowerShell can't find it.

Add the CLI to your System Variables PATH. 
Usually, you can find the CLI in: `C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\`
'''



import os
from dotenv import load_dotenv
from typing import Any
from pathlib import Path


# Add references
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FilePurpose, CodeInterpreterTool, ListSortOrder, MessageRole


def main(): 

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    project_endpoint= os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

    # Display the data to be analyzed
    script_dir = Path(__file__).parent  # Get the directory of the script
    file_path = script_dir / 'Data' / 'data.txt'

    with file_path.open('r') as file:
        data = file.read() + "\n"
        print(data)

    # Connect to the Agent client
    agent_client = AgentsClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential
            (exclude_environment_credential=True,
            exclude_managed_identity_credential=True)
    )
    with agent_client:


        # Upload the data file and create a CodeInterpreterTool
        file = agent_client.files.upload_and_poll(
            file_path=file_path, purpose=FilePurpose.AGENTS
        )
        print(f"Uploaded {file.filename}")

        code_interpreter = CodeInterpreterTool(file_ids=[file.id])


        # Define an agent that uses the CodeInterpreterTool
        agent = agent_client.create_agent(
            model=model_deployment,
            name="data-agent",
            instructions="You are an AI agent that analyzes the data in the file that has been uploaded. Use Python to calculate statistical metrics as necessary.",
            tools=code_interpreter.definitions,
            tool_resources=code_interpreter.resources,
        )
        print(f"Using agent: {agent.name}")


        # Create a thread for the conversation
        thread = agent_client.threads.create()

    
        # Loop until the user types 'quit'
        while True:
            # Get input text
            user_prompt = input("Enter a prompt (or type 'quit' to exit): ")
            if user_prompt.lower() == "quit":
                break
            if len(user_prompt) == 0:
                print("Please enter a prompt.")
                continue

            # Send a prompt to the agent
            message = agent_client.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_prompt,
            )

            run = agent_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)


            # Check the run status for failures
            if run.status == "failed":
                print(f"Run failed: {run.last_error}")

    
            # Show the latest response from the agent
            last_msg = agent_client.messages.get_last_message_text_by_role(
                thread_id=thread.id,
                role=MessageRole.AGENT,
            )
            if last_msg:
                print(f"Last Message: {last_msg.text.value}")


        # Get the conversation history
        print("\nConversation Log:\n")
        messages = agent_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        for message in messages:
            if message.text_messages:
                last_msg = message.text_messages[-1]
                print(f"{message.role}: {last_msg.text.value}\n")
    

        # Clean up
        agent_client.delete_agent(agent.id)

    


if __name__ == '__main__': 
    main()


'''
Example Conversation Log:

MessageRole.USER: what's the category with the highest cost?

MessageRole.AGENT: Let me first inspect the uploaded file to understand its structure and contents. Then, I'll identify the category with the highest cost.

MessageRole.AGENT: The uploaded file contains two columns: `Category` and `Cost`. To determine the category with the highest cost, I'll find the category with the maximum value in the `Cost` column.

MessageRole.AGENT: The category with the highest cost is **Transportation**, with a total cost of **2301.00**.

MessageRole.USER: Create a text-based bar chart showing cost by category

MessageRole.AGENT: Here is a text-based bar chart showing the costs by category:

```
Transportation: ████████████████████████████████████████ (2301.0)
Accommodation: ███████████ (674.56)
Meals: ████ (267.89)
Misc.:  (34.5)
```

This chart proportionally represents each category's cost with bars relative to the highest cost (Transportation).
'''