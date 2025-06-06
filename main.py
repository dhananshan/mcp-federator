import asyncio
import json
from string import Template
import os
import logging
from agents import Agent, Runner, gen_trace_id, trace, AsyncOpenAI, OpenAIChatCompletionsModel,set_tracing_disabled
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI

logging.basicConfig(level=logging.WARNING)

# set to false because openapi try to send trace to openapi server rather than azure openapi server. possible bug in openapi library
set_tracing_disabled(disabled=True)

async def main():
    """
    Asynchronous entry point for the MCP Federator application.
    This function performs the following steps:
    1. Loads environment variables from a .env file.
    2. Loads and processes the application configuration from 'config.json', recursively substituting environment variables.
    3. Initializes MCP server instances based on the configuration.
    4. Configures the Azure OpenAI client and model, or optionally a local model.
    5. Initializes the agent with the specified configuration and MCP servers.
    6. Enters a chat loop, accepting user prompts, maintaining chat history, and generating responses using the agent.
    7. Supports graceful exit on user command.
    Returns:
        None
    Raises:
        Any exceptions raised during configuration loading, server initialization, or agent execution.
    """

    load_dotenv()

    # Load MCP server configs from config.json
    with open("config.json", "r") as f:
        config = json.load(f)

    # Recursively substitute environment variables in the config
    def substitute_env_in_obj(obj):
        if isinstance(obj, dict):
            return {k: substitute_env_in_obj(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [substitute_env_in_obj(item) for item in obj]
        elif isinstance(obj, str):
            return Template(obj).safe_substitute(os.environ)
        else:
            return obj

    config = substitute_env_in_obj(config)

    # Initialize array of MCPServerStdio from config
    mcp_servers = [
        MCPServerStdio(
            name=server_conf.get("name"), 
            params={
            "command": server_conf["command"],
            "args": server_conf["args"],
            "env":  server_conf["env"]
            }
        )
        for server_conf in config["mcp_servers"]
    ]

    azure_openai_conf = config.get("azure_openai", {})
    
    client = AsyncAzureOpenAI(
            api_key=azure_openai_conf.get("api_key"),
            api_version=azure_openai_conf.get("api_version"),
            azure_endpoint=azure_openai_conf.get("api_host")
    )
    
    # Configure the model
    model = OpenAIChatCompletionsModel( 
            model=azure_openai_conf.get("deployment_name"),	
            openai_client=client,
    )

    #If you want o test with your local mode (e.g. llama.cpp), you can use the following line instead:
    # model = OpenAIChatCompletionsModel( 
    #     model="llama3.1",
    #     openai_client=AsyncOpenAI(base_url="http://localhost:11434/v1")
    # )

    agent_conf = config.get("agent", {})

    async with asyncio.TaskGroup() as tg:
        servers = [await tg.create_task(server.__aenter__()) for server in mcp_servers]

    trace_id = gen_trace_id()

    with trace(workflow_name=agent_conf.get("workflow_name"), trace_id=trace_id):
        agent = Agent(
            name=agent_conf.get("name"),
            instructions=" ".join(agent_conf.get("instructions")) if isinstance(agent_conf.get("instructions"), list) else agent_conf.get("instructions"),
            mcp_servers=servers,
            model=model
        )

        #for chat history
        chat_history = []
        
        while True:
            prompt = input("Enter a prompt (type 'exit' to quit): ")
            if prompt.strip().lower() in ("exit", "quit"):
                print("Exiting chat.")
                break
            # Add user prompt to chat history
            chat_history.append({"role": "user", "content": prompt})
            # Pass chat history as input
            result = await Runner.run(starting_agent=agent, input=chat_history)
            print(result.final_output)
            # Add agent response to chat history
            chat_history.append({"role": "assistant", "content": result.final_output})
        
if __name__ == "__main__":
    asyncio.run(main())