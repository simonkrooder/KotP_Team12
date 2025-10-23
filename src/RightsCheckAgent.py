
import asyncio
import logging
import os
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    AsyncFunctionTool,
    MessageRole,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

API_DEPLOYMENT_NAME = os.getenv("AGENT_MODEL_DEPLOYMENT_NAME")
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
AZURE_RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP_NAME")
TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.2"))

if not (API_DEPLOYMENT_NAME and PROJECT_ENDPOINT and AZURE_SUBSCRIPTION_ID and AZURE_RESOURCE_GROUP):
    logger.error("Missing required environment variables. Please check your .env file.")
    exit(1)

project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

def check_authorization(user_id: str, system: str, access_level: str) -> dict:
    from src import data_access
    try:
        df = data_access.read_csv('authorisations')
        match = df[(df['user_id'] == user_id) & (df['system'] == system) & (df['access_level'] == access_level)]
        authorized = not match.empty
        evidence = match.to_dict(orient="records") if authorized else []
        return {"authorized": authorized, "evidence": evidence, "message": "Authorized" if authorized else "Not authorized"}
    except Exception as e:
        logger.error(f"check_authorization failed: {e}")
        return {"authorized": False, "evidence": [], "message": str(e)}

def lookup_data(file: str, query: dict) -> dict:
    from src import data_access
    try:
        df = data_access.read_csv(file)
        for k, v in query.items():
            df = df[df[k] == v]
        return {"results": df.to_dict(orient="records")}
    except Exception as e:
        logger.error(f"lookup_data failed: {e}")
        return {"results": [], "error": str(e)}

def get_toolset():
    async def async_check_authorization(user_id: str, system: str, access_level: str) -> dict:
        return await asyncio.to_thread(check_authorization, user_id, system, access_level)
    async def async_lookup_data(file: str, query: dict) -> dict:
        return await asyncio.to_thread(lookup_data, file, query)
    return AsyncFunctionTool(functions={
        async_check_authorization,
        async_lookup_data,
    })

def load_instructions():
    return "You are a rights check agent. Use the available tools to check user rights and provide recommendations."

async def initialize():
    instructions = load_instructions()
    toolset = get_toolset()
    logger.info("Creating agent...")
    agent = project_client.agents.create_agent(
        model=API_DEPLOYMENT_NAME,
        name="RightsCheckAgent",
        instructions=instructions,
        toolset=toolset,
        temperature=TEMPERATURE,
        headers={"x-ms-enable-preview": "true"},
    )
    logger.info(f"Created agent, ID: {agent.id}")
    thread = project_client.agents.threads.create()
    logger.info(f"Created thread, ID: {thread.id}")
    return agent, thread

async def post_message(agent, thread_id, content, thread):
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
    from src.agent_protocol import create_message, log_agent_message
    while run.status in ("queued", "in_progress", "requires_action") and iteration < max_iterations:
        await asyncio.sleep(2)
        iteration += 1
        run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
        logger.info(f"Run status: {run.status} (iteration {iteration})")
        if run.status == "requires_action" and run.required_action:
            logger.info("Run requires action - handling tool calls...")
            tool_outputs = []
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                logger.info(f"Executing function: {tool_call.function.name}")
                args = json.loads(tool_call.function.arguments)
                retries = 0
                max_retries = 3
                result = None
                while retries < max_retries:
                    try:
                        if tool_call.function.name == "async_check_authorization":
                            result = await get_toolset().tools[0].coroutine(**args)
                        elif tool_call.function.name == "async_lookup_data":
                            result = await get_toolset().tools[1].coroutine(**args)
                        else:
                            result = f"Tool {tool_call.function.name} not implemented."
                        # Log successful tool call
                        msg = create_message(
                            sender="RightsCheckAgent",
                            receiver="ToolCall",
                            action=tool_call.function.name,
                            context=args,
                            status="success",
                            error=None
                        )
                        log_agent_message(msg, comment=f"Tool call success")
                        break
                    except Exception as e:
                        retries += 1
                        msg = create_message(
                            sender="RightsCheckAgent",
                            receiver="ToolCall",
                            action=tool_call.function.name,
                            context=args,
                            status="error",
                            error={"message": str(e), "retry": retries}
                        )
                        log_agent_message(msg, comment=f"Tool call error, retry {retries}")
                        logger.error(f"Error in tool call {tool_call.function.name}: {e} (retry {retries})")
                        if retries >= max_retries:
                            result = {"error": str(e), "retries": retries}
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

async def main():
    with project_client:
        agent, thread = await initialize()
        while True:
            print("\nEnter your rights check context (type exit to finish): ", end="")
            prompt = await asyncio.to_thread(input)
            if prompt.lower() == "exit":
                break
            if not prompt.strip():
                continue
            await post_message(agent=agent, thread_id=thread.id, content=prompt, thread=thread)
        print("Cleaning up...")

if __name__ == "__main__":
    asyncio.run(main())
