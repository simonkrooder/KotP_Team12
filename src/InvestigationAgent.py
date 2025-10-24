
import os
import logging
import sys
import asyncio
from pathlib import Path
from datetime import datetime
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
        from src.agent_protocol import create_message, log_agent_message

        def log_to_file(message: str):
            log_path = os.path.join(os.path.dirname(__file__), 'log.txt')
            with open(log_path, 'a', encoding='utf-8') as logf:
                logf.write(message + '\n')

        # --- InvestigationAgent step ---
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

        investigation_result = None
        if run.status == "completed":
            response = self.project_client.agents.messages.get_last_message_by_role(
                thread_id=self.thread.id,
                role=MessageRole.AGENT,
            )
            if response:
                investigation_result = {
                    "agent": "InvestigationAgent",
                    "status": "completed",
                    "response": "\n".join(t.text.value for t in response.text_messages),
                    "context": context
                }
            else:
                investigation_result = {
                    "agent": "InvestigationAgent",
                    "status": "error",
                    "error": "No response message found.",
                    "context": context
                }
        elif run.status == "failed":
            investigation_result = {
                "agent": "InvestigationAgent",
                "status": "error",
                "error": str(run.last_error),
                "context": context
            }

        # --- Agent2Agent: Call RightsCheckAgent ---
        # Import here to avoid circular import at module level
        import traceback
        try:
            from src.RightsCheckAgent import RightsCheckAgent
            rights_agent = RightsCheckAgent()
            # Log the agent-to-agent message
            msg = create_message(
                sender="InvestigationAgent",
                receiver="RightsCheckAgent",
                action="handle_request",
                context=context,
                status="pending"
            )
            log_agent_message(msg, comment="InvestigationAgent delegating to RightsCheckAgent")
            # Call RightsCheckAgent synchronously (it will run its own async loop)
            rights_result = await rights_agent.handle_request(context)
            # Log the response (audit trail)
            msg2 = create_message(
                sender="RightsCheckAgent",
                receiver="InvestigationAgent",
                action="response",
                context=rights_result,
                status=rights_result.get("status", "unknown")
            )
            log_agent_message(msg2, comment="RightsCheckAgent response to InvestigationAgent")
            # Explicit audit trail: InvestigationAgent receives RightsCheckAgent response
            msg3 = create_message(
                sender="InvestigationAgent",
                receiver="InvestigationAgent",
                action="received_rightscheck_response",
                context=rights_result,
                status=rights_result.get("status", "unknown")
            )
            log_agent_message(msg3, comment="InvestigationAgent received response from RightsCheckAgent")
            logger.info(f"InvestigationAgent received response from RightsCheckAgent: {rights_result}")
        except Exception as e:
            tb_str = traceback.format_exc()
            logger.error(f"Failed to call RightsCheckAgent: {e}\n{tb_str}")
            # Also log to /src/log.txt
            log_path = os.path.join(os.path.dirname(__file__), 'log.txt')
            with open(log_path, 'a', encoding='utf-8') as logf:
                logf.write(f"[RightsCheckAgent ERROR] {datetime.utcnow().isoformat()}\n{tb_str}\n")
            rights_result = {
                "agent": "RightsCheckAgent",
                "status": "error",
                "error": f"Failed to call RightsCheckAgent: {e}",
                "context": context
            }
            msg = create_message(
                sender="InvestigationAgent",
                receiver="RightsCheckAgent",
                action="handle_request",
                context=context,
                status="error",
                error={"message": str(e), "traceback": tb_str}
            )
            log_agent_message(msg, comment="Error calling RightsCheckAgent")

        # --- Return combined result ---
        return {
            "investigation": investigation_result,
            "rights_check": rights_result
        }

# --- MAIN BLOCK ---
if __name__ == "__main__":
    import json
    import sys
    import asyncio
    print("InvestigationAgent CLI. Choose mode:")
    print("1. Chat mode (plain text, conversational)")
    print("2. JSON mode (enter raw JSON context)")
    mode = None
    while mode not in ("1", "2"):
        mode = input("Select mode [1/2]: ").strip()
    agent = InvestigationAgent()
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
                "history": history[-10:]  # last 10 turns for context
            }
            result = await agent._handle_request_async(context)
            agent_reply = result.get("response") or result.get("error") or "(no response)"
            print(f"Agent: {agent_reply}\n")
            # Add to history
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