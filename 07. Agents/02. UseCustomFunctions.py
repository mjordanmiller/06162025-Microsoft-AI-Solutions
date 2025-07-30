'''
This script demonstrates how to use custom functions with an agent in Azure AI.
You’ll build a simple technical support agent that can collect details of a technical problem and generate a support ticket.
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

'''
NOTE:
RUNNING THE CODE:
When prompted, enter a prompt such as:
- I have a technical problem
View the response. 
The agent may ask for your email address and a description of the issue.
You can use any email address (for example, jordan@contoso.com) and any issue description (for example my computer won't start)

When it has enough information, the agent should choose to use your function as required.
A txt file will be created in the same directory as this script, with the support ticket details.
'''


import os
from dotenv import load_dotenv
from typing import Any
from pathlib import Path


# Add references
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, ToolSet, ListSortOrder, MessageRole
from user_functions import user_functions

def main(): 

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    project_endpoint= os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")


    # Connect to the Agent client
    agent_client = AgentsClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential
            (exclude_environment_credential=True,
            exclude_managed_identity_credential=True)
    )
    


    # Define an agent that can use the custom functions
    with agent_client:

        functions = FunctionTool(user_functions)
        toolset = ToolSet()
        toolset.add(functions)
        agent_client.enable_auto_function_calls(toolset)
                
        agent = agent_client.create_agent(
            model=model_deployment,
            name="support-agent",
            instructions="""You are a technical support agent.
                            When a user has a technical issue, you get their email address and a description of the issue.
                            Then you use those values to submit a support ticket using the function available to you.
                            If a file is saved, tell the user the file name.
                        """,
            toolset=toolset
        )

        thread = agent_client.threads.create()
        print(f"You're chatting with: {agent.name} ({agent.id})")



    
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
                content=user_prompt
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
        print("Deleted agent")

    



if __name__ == '__main__': 
    main()



'''
Example OUTPUT:
Conversation Log:

MessageRole.USER: I have a technical problem

MessageRole.AGENT: Could you please provide your email address and describe the issue you're facing so I can help submit a support ticket for you?

MessageRole.USER: jmiller@skillstorm.com and I am having issues getting on the company network

MessageRole.AGENT: Your support ticket has been successfully submitted. The ticket file is saved as **ticket-2afd49.txt**. Someone from support will get back to you soon!

Deleted agent
'''
