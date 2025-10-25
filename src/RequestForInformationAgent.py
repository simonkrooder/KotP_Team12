
# --- RequestForInformationAgent tool functions and helpers ---
import asyncio
import logging
import os
import sys
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import AsyncFunctionTool, MessageRole
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Ensure project root is in sys.path for 'src' imports when run as __main__
if __name__ == "__main__":
    project_root = str(Path(__file__).resolve().parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

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

def notify_send(recipient_id: str, subject: str, body: str, context: dict = None) -> dict:
    import uuid
    notification_id = str(uuid.uuid4())
    logger.info(f"[MOCK] Notification sent to {recipient_id}: {subject} | {body}")
    # Simulate a response from the recipient
    mock_response = f"Received request: '{subject}'. Reason provided: 'Change required by management.'"
    return {
        "status": "sent",
        "message_id": notification_id,
        "message": f"Notification sent to {recipient_id}",
        "recipient_id": recipient_id,
        "subject": subject,
        "body": body,
        "context": context,
        "response": mock_response
    }

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
    async def async_notify_send(recipient_id: str, subject: str, body: str, context: dict = None) -> dict:
        return await asyncio.to_thread(notify_send, recipient_id, subject, body, context)
    async def async_lookup_data(file: str, query: dict = None) -> dict:
        if query is None:
            logger.error("async_lookup_data called without required 'query' argument.")
            return {"results": [], "error": "Missing required argument: 'query'"}
        return await asyncio.to_thread(lookup_data, file, query)
    async_tool = AsyncFunctionTool(functions=[async_notify_send, async_lookup_data])
    tool_map = {
        "async_notify_send": async_notify_send,
        "async_lookup_data": async_lookup_data
    }
    return async_tool, tool_map

def load_instructions():
    return "You are the Request for Information Agent. Use send_notification and lookup_data to contact users/managers and validate claims."


class RequestForInformationAgent:
    def __init__(self):
        self.project_client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=DefaultAzureCredential(),
        )
        self.agent = None
        self.thread = None
        self.initialized = False

    async def initialize(self):
        instructions = load_instructions()
        async_tool, _ = get_toolset()
        logger.info("Creating agent...")
        self.agent = self.project_client.agents.create_agent(
            model=API_DEPLOYMENT_NAME,
            name="RequestForInformationAgent",
            instructions=instructions,
            toolset=async_tool,
            temperature=TEMPERATURE,
            headers={"x-ms-enable-preview": "true"},
        )
        logger.info(f"Created agent, ID: {self.agent.id}")
        self.thread = self.project_client.agents.threads.create()
        logger.info(f"Created thread, ID: {self.thread.id}")
        self.initialized = True

    async def handle_request(self, context: dict) -> dict:
        return await self._handle_request_async(context)

    async def _handle_request_async(self, context: dict) -> dict:
        if not self.initialized:
            await self.initialize()
        import json
        message = self.project_client.agents.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=json.dumps(context),
        )
        run = self.project_client.agents.runs.create(
            thread_id=self.thread.id,
            agent_id=self.agent.id,
        )
        max_iterations = 60
        iteration = 0
        from src.agent_protocol import create_message, log_agent_message
        def ensure_mutation_id(ctx):
            ctx = dict(ctx) if ctx else {}
            if 'mutation_id' not in ctx:
                # Try to infer from nested context
                for v in ctx.values():
                    if isinstance(v, dict) and 'mutation_id' in v:
                        ctx['mutation_id'] = v['mutation_id']
                        break
                if 'mutation_id' not in ctx:
                    ctx['mutation_id'] = 'unknown'
            return ctx
        _, tool_map = get_toolset()
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
                            if tool_call.function.name in tool_map:
                                result = await tool_map[tool_call.function.name](**args)
                            else:
                                result = f"Tool {tool_call.function.name} not implemented."
                            msg = create_message(
                                sender="RequestForInformationAgent",
                                receiver="ToolCall",
                                action=tool_call.function.name,
                                context=ensure_mutation_id(args),
                                status="success",
                                error=None
                            )
                            log_agent_message(msg, comment="Tool call success")
                            break
                        except Exception as e:
                            retries += 1
                            error_msg = f"Error in tool call {tool_call.function.name} with args {args}: {e} (retry {retries})"
                            msg = create_message(
                                sender="RequestForInformationAgent",
                                receiver="ToolCall",
                                action=tool_call.function.name,
                                context=ensure_mutation_id(args),
                                status="error",
                                error={"message": str(e), "retry": retries, "args": args}
                            )
                            log_agent_message(msg, comment=error_msg)
                            logger.error(error_msg)
                            if retries >= max_retries:
                                result = {"error": str(e), "retries": retries, "args": args}
                    # Ensure output is a string (JSON-encoded if not already)
                    output_str = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": output_str
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
                    "agent": "RequestForInformationAgent",
                    "status": "completed",
                    "response": "\n".join(t.text.value for t in response.text_messages),
                    "context": context
                }
            else:
                return {
                    "agent": "RequestForInformationAgent",
                    "status": "error",
                    "error": "No response message found.",
                    "context": context
                }
        elif run.status == "failed":
            return {
                "agent": "RequestForInformationAgent",
                "status": "error",
                "error": str(run.last_error),
                "context": context
            }


# --- MAIN BLOCK ---
if __name__ == "__main__":
    import json
    import sys
    import asyncio
    print("RequestForInformationAgent CLI. Choose mode:")
    print("1. Chat mode (plain text, conversational)")
    print("2. JSON mode (enter raw JSON context)")
    mode = None
    while mode not in ("1", "2"):
        mode = input("Select mode [1/2]: ").strip()
    agent = RequestForInformationAgent()
    async def chat_cli_loop():
        await agent.initialize()
        print("\nChat mode: Type your message and press Enter. Type 'exit' to quit.")
        history = []
        while True:
            try:
                user_input = input("You: ")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break
            if user_input.strip().lower() == "exit":
                break
            if not user_input.strip():
                continue
            # Build context with message and history
            context = {
                "message": user_input,
                "history": history[-10:]
            }
            result = await agent._handle_request_async(context)
            agent_reply = result.get("response") or result.get("error") or "(no response)"
            print(f"Agent: {agent_reply}\n")
            history.append({"role": "user", "content": user_input})
            history.append({"role": "agent", "content": agent_reply})

    async def json_cli_loop():
        await agent.initialize()
        print("\nJSON mode: Enter context as JSON. Type 'exit' to quit.")
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

    if mode == "1":
        asyncio.run(chat_cli_loop())
    else:
        asyncio.run(json_cli_loop())
