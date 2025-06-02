import asyncio
import logging
import os 
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.mcp import MCPStdioPlugin

from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from dotenv import load_dotenv



# Load environment variables from .env file
load_dotenv()


async def main():
    # Initialize the kernel
    kernel = Kernel()

    # Add Azure OpenAI chat completion
    chat_completion = AzureChatCompletion()
    kernel.add_service(chat_completion)



    # Set the logging level for  semantic_kernel.kernel to DEBUG.
    logging.basicConfig(
        format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("kernel").setLevel(logging.ERROR)
    print("$HA_API_ACCESS_TOKEN")

    ha_plugin = MCPStdioPlugin(
        name="homeassistant",
        description="Home Assistant Plugin",
        command="mcp-proxy",
        #args=["-y", "@modelcontextprotocol/server-github"],
        env={
            "SSE_URL": "http://10.1.1.224:8123/mcp_server/sse",
            "API_ACCESS_TOKEN": os.environ.get("HA_API_ACCESS_TOKEN", ""),
            "DEBUG": "false",  # Enable debug mode for the MCP plugin
            "NODE_DEBUG": "false"  # Debug for Node.js subprocess
        },
        )
    await ha_plugin.connect() 

    # Add the plugin to the kernel
    kernel.add_plugin(ha_plugin)
    


    # Enable planning
    execution_settings = AzureChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    # Create a history of the conversation
    history = ChatHistory()

    # Initiate a back-and-forth chat
    userInput = None
    while True:
        # Collect user input
        userInput = input("User > ")

        # Terminate the loop if the user says "exit"
        if userInput == "exit":
            break

        # Add user input to the history
        history.add_user_message(userInput)

        # Get the response from the AI
        result = await chat_completion.get_chat_message_content(
            chat_history=history,
            settings=execution_settings,
            kernel=kernel,
        )

        # Print the results
        print("Assistant > " + str(result))

        # Add the message from the agent to the chat history
        history.add_message(result)


    await ha_plugin.close()

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
