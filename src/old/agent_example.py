import asyncio
import logging
import os
from azure.ai.projects import AIProjectClient
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    Agent,
    AgentThread,
    AsyncFunctionTool,
    AsyncToolSet,
    MessageRole,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from /src/.env (absolute path)
from pathlib import Path
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

API_DEPLOYMENT_NAME = os.getenv("AGENT_MODEL_DEPLOYMENT_NAME")
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
# Use AZURE_RESOURCE_GROUP_NAME as in .env
AZURE_RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP_NAME")
TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.2"))

if not (API_DEPLOYMENT_NAME and PROJECT_ENDPOINT and AZURE_SUBSCRIPTION_ID and AZURE_RESOURCE_GROUP):
    logger.error("Missing required environment variables. Please check your .env file.")
    exit(1)

# Initialize Azure AI Project client
project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

# Tool stubs (implement your own logic here)
def fetch_hr_mutation_data(query: str) -> str:
    # TODO: Implement actual data access logic
    return f"Fetched HR mutation data for query: {query}"

def fetch_user_authorizations(user_id: str) -> str:
    # TODO: Implement actual data access logic
    return f"Fetched authorizations for user: {user_id}"

# Register tools
def get_toolset():
    import asyncio
    async def async_fetch_hr_mutation_data(query: str) -> str:
        return await asyncio.to_thread(fetch_hr_mutation_data, query)
    async def async_fetch_user_authorizations(user_id: str) -> str:
        return await asyncio.to_thread(fetch_user_authorizations, user_id)
    return AsyncFunctionTool(functions={
        async_fetch_hr_mutation_data,
        async_fetch_user_authorizations,
        # Add more async functions as needed
    })

# Load agent instructions (can be from a file or string)
def load_instructions():
    instructions_path = os.path.join(os.path.dirname(__file__), "agent_instructions.txt")
    if os.path.exists(instructions_path):
        with open(instructions_path, "r", encoding="utf-8") as f:
            return f.read()
    # Fallback: default instructions
    return "You are an access control investigation agent. Use the available tools to gather data, reason, and provide recommendations."

async def initialize():
    try:
        instructions = load_instructions()
        toolset = get_toolset()
        logger.info("Creating agent...")
        agent = project_client.agents.create_agent(
            model=API_DEPLOYMENT_NAME,
            name="Access Control Agent",
            instructions=instructions,
            toolset=toolset,
            temperature=TEMPERATURE,
            headers={"x-ms-enable-preview": "true"},
        )
        logger.info(f"Created agent, ID: {agent.id}")
        logger.info("Creating thread...")
        thread = project_client.agents.threads.create()
        logger.info(f"Created thread, ID: {thread.id}")
        return agent, thread
    except Exception as e:
        logger.error(f"Error initializing agent: {e}")
        raise

async def post_message(agent, thread_id, content, thread):
    try:
        logger.info(f"Posting message to thread {thread_id}...")
        message = project_client.agents.messages.create(
            thread_id=thread_id,
            role="user",
            content=content,
        )
        logger.info(f"Message created: {message.id}")
        run = project_client.agents.runs.create(
            thread_id=thread.id,
            agent_id=agent.id,
        )
        logger.info(f"Run created: {run.id}")
        import json
        max_iterations = 60
        iteration = 0
        while run.status in ("queued", "in_progress", "requires_action") and iteration < max_iterations:
            await asyncio.sleep(2)
            iteration += 1
            run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
            logger.info(f"Run status: {run.status} (iteration {iteration})")
            # Handle required actions (tool calls)
            if run.status == "requires_action" and run.required_action:
                logger.info("Run requires action - handling tool calls...")
                tool_outputs = []
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    logger.info(f"Executing function: {tool_call.function.name}")
                    args = json.loads(tool_call.function.arguments)
                    # Dispatch to the correct tool
                    if tool_call.function.name == "fetch_hr_mutation_data":
                        result = await get_toolset().tools[0].coroutine(**args)
                    elif tool_call.function.name == "fetch_user_authorizations":
                        result = await get_toolset().tools[1].coroutine(**args)
                    else:
                        result = f"Tool {tool_call.function.name} not implemented."
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": result
                    })
                if tool_outputs:
                    run = project_client.agents.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                    logger.info("Tool outputs submitted.")
        if run.status == "completed":
            # Get the last message from the agent
            response = project_client.agents.messages.get_last_message_by_role(
                thread_id=thread_id,
                role=MessageRole.AGENT,
            )
            if response:
                print("\nAgent response:")
                print("\n".join(t.text.value for t in response.text_messages))
            else:
                print("No response message found.")
        elif run.status == "failed":
            print(f"Run failed: {run.last_error}")
    except Exception as e:
        logger.error(f"Error posting message: {e}")

async def main():
    with project_client:
        agent, thread = await initialize()
        while True:
            print("\nEnter your query (type exit to finish): ", end="")
            prompt = await asyncio.to_thread(input)
            if prompt.lower() == "exit":
                break
            if not prompt.strip():
                continue
            await post_message(agent=agent, thread_id=thread.id, content=prompt, thread=thread)
        print("Cleaning up...")
        # Optionally: cleanup agent/thread if needed

if __name__ == "__main__":
    asyncio.run(main())