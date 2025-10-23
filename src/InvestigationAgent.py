import os
import logging
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import AsyncFunctionTool, MessageRole
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from pathlib import Path
import asyncio

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

# Example tool function
async def lookup_data(file: str, query: dict) -> dict:
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
    return AsyncFunctionTool(functions=[lookup_data])

class InvestigationAgent:
    def __init__(self):
        self.project_client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=DefaultAzureCredential(),
        )
        self.agent = None
        self.thread = None
        self.initialized = False

    async def initialize(self):
        toolset = get_toolset()
        logger.info("Creating agent...")
        self.agent = self.project_client.agents.create_agent(
            model=API_DEPLOYMENT_NAME,
            name="InvestigationAgent",
            instructions="You are the Investigation Agent. Use lookup_data as needed.",
            toolset=toolset,
            temperature=TEMPERATURE,
            headers={"x-ms-enable-preview": "true"},
        )
        logger.info(f"Created agent, ID: {self.agent.id}")
        self.thread = self.project_client.agents.threads.create()
        logger.info(f"Created thread, ID: {self.thread.id}")
        self.initialized = True

    def handle_request(self, context: dict) -> dict:
        # Synchronous entrypoint for orchestrator
        return asyncio.run(self._handle_request_async(context))

    async def _handle_request_async(self, context: dict) -> dict:
        if not self.initialized:
            await self.initialize()
        import json
        message = self.project_client.agents.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=context,
        )
        run = self.project_client.agents.runs.create(
            thread_id=self.thread.id,
            agent_id=self.agent.id,
        )
        max_iterations = 60
        iteration = 0
        from src.agent_protocol import create_message, log_agent_message
        while run.status in ("queued", "in_progress", "requires_action") and iteration < max_iterations:
            await asyncio.sleep(2)
            iteration += 1
            run = self.project_client.agents.runs.get(thread_id=self.thread.id, run_id=run.id)
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
                            # Call the registered tool function
                            result = await lookup_data(**args)
                            msg = create_message(
                                sender="InvestigationAgent",
                                receiver="ToolCall",
                                action=tool_call.function.name,
                                context=args,
                                status="success",
                                error=None
                            )
                            log_agent_message(msg, comment="Tool call success")
                            break
                        except Exception as e:
                            retries += 1
                            msg = create_message(
                                sender="InvestigationAgent",
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
                    run = self.project_client.agents.runs.submit_tool_outputs(
                        thread_id=self.thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                    logger.info("Tool outputs submitted.")
        if run.status == "completed":
            response = self.project_client.agents.messages.get_last_message_by_role(
                thread_id=self.thread.id,
                role=MessageRole.AGENT,
            )
            if response:
                return {
                    "agent": "InvestigationAgent",
                    "status": "completed",
                    "response": "\n".join(t.text.value for t in response.text_messages),
                    "context": context
                }
            else:
                return {
                    "agent": "InvestigationAgent",
                    "status": "error",
                    "error": "No response message found.",
                    "context": context
                }
        elif run.status == "failed":
            return {
                "agent": "InvestigationAgent",
                "status": "error",
                "error": str(run.last_error),
                "context": context
            }

# --- MAIN BLOCK ---
if __name__ == "__main__":
    import json
    import sys
    import asyncio
    print("InvestigationAgent CLI. Enter context as JSON or type 'exit' to quit.")
    agent = InvestigationAgent()
    async def cli_loop():
        await agent.initialize()
        while True:
            try:
                user_input = input("\nEnter context JSON (or 'exit'): ")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break
            if user_input.strip().lower() == "exit":
                break
            if not user_input.strip():
                continue
            try:
                context = json.loads(user_input)
            except Exception as e:
                print(f"Invalid JSON: {e}")
                continue
            result = await agent._handle_request_async(context)
            print("\nAgent response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
    asyncio.run(cli_loop())