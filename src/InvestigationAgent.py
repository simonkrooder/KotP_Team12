
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
        reasoning_text = None
        if run.status == "completed":
            response = self.project_client.agents.messages.get_last_message_by_role(
                thread_id=self.thread.id,
                role=MessageRole.AGENT,
            )
            if response:
                reasoning_text = "\n".join(t.text.value for t in response.text_messages)
                investigation_result = {
                    "agent": "InvestigationAgent",
                    "status": "completed",
                    "response": reasoning_text,
                    "context": context,
                    "reasoning": reasoning_text
                }
            else:
                investigation_result = {
                    "agent": "InvestigationAgent",
                    "status": "error",
                    "error": "No response message found.",
                    "context": context,
                    "reasoning": ""
                }
        elif run.status == "failed":
            investigation_result = {
                "agent": "InvestigationAgent",
                "status": "error",
                "error": str(run.last_error),
                "context": context,
                "reasoning": str(run.last_error)
            }
        # Log reasoning to audit trail
        import json as _json
        reasoning_serialized = _json.dumps(investigation_result.get("reasoning", ""), ensure_ascii=False)
        msg_reasoning = create_message(
            sender="InvestigationAgent",
            receiver="AuditTrail",
            action="reasoning",
            context={**context, "reasoning": reasoning_serialized},
            status=investigation_result.get("status", "unknown")
        )
        log_agent_message(msg_reasoning, comment="InvestigationAgent reasoning step")

        # --- Agent2Agent: Call RightsCheckAgent ---
        import traceback
        rights_result = None
        try:
            from src.RightsCheckAgent import RightsCheckAgent
            rights_agent = RightsCheckAgent()
            msg = create_message(
                sender="InvestigationAgent",
                receiver="RightsCheckAgent",
                action="handle_request",
                context=context,
                status="pending"
            )
            log_agent_message(msg, comment="InvestigationAgent delegating to RightsCheckAgent")
            rights_result = await rights_agent.handle_request(context)
            # Log reasoning for RightsCheckAgent step
            import json as _json
            rights_reasoning = rights_result.get("response") or rights_result.get("error") or rights_result.get("status")
            rights_reasoning_serialized = _json.dumps(rights_reasoning, ensure_ascii=False)
            msg2 = create_message(
                sender="RightsCheckAgent",
                receiver="InvestigationAgent",
                action="response",
                context={**rights_result, "reasoning": rights_reasoning_serialized},
                status=rights_result.get("status", "unknown")
            )
            log_agent_message(msg2, comment="RightsCheckAgent response to InvestigationAgent")
            msg3 = create_message(
                sender="InvestigationAgent",
                receiver="InvestigationAgent",
                action="received_rightscheck_response",
                context={**rights_result, "reasoning": rights_reasoning_serialized},
                status=rights_result.get("status", "unknown")
            )
            log_agent_message(msg3, comment="InvestigationAgent received response from RightsCheckAgent")
            logger.info(f"InvestigationAgent received response from RightsCheckAgent: {rights_result}")
        except Exception as e:
            tb_str = traceback.format_exc()
            logger.error(f"Failed to call RightsCheckAgent: {e}\n{tb_str}")
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

        # --- Agent2Agent: Step 1: Ask RequestForInformationAgent for user clarification ---
        info_user_result = None
        try:
            from src.RequestForInformationAgent import RequestForInformationAgent
            info_agent = RequestForInformationAgent()
            msg = create_message(
                sender="InvestigationAgent",
                receiver="RequestForInformationAgent",
                action="request_user_clarification",
                context=context,
                status="pending"
            )
            log_agent_message(msg, comment="InvestigationAgent delegating to RequestForInformationAgent for user clarification")
            info_user_result = await info_agent.handle_request({**context, "clarification_type": "user"})
            # Log reasoning for RequestForInformationAgent (user) step
            import json as _json
            info_user_reasoning = info_user_result.get("response") or info_user_result.get("error") or info_user_result.get("status")
            info_user_reasoning_serialized = _json.dumps(info_user_reasoning, ensure_ascii=False)
            msg2 = create_message(
                sender="RequestForInformationAgent",
                receiver="InvestigationAgent",
                action="response_user_clarification",
                context={**info_user_result, "reasoning": info_user_reasoning_serialized},
                status=info_user_result.get("status", "unknown")
            )
            log_agent_message(msg2, comment="RequestForInformationAgent response to InvestigationAgent (user clarification)")
            msg3 = create_message(
                sender="InvestigationAgent",
                receiver="InvestigationAgent",
                action="received_informationagent_user_response",
                context={**info_user_result, "reasoning": info_user_reasoning_serialized},
                status=info_user_result.get("status", "unknown")
            )
            log_agent_message(msg3, comment="InvestigationAgent received response from RequestForInformationAgent (user clarification)")
            logger.info(f"InvestigationAgent received response from RequestForInformationAgent (user clarification): {info_user_result}")
        except Exception as e:
            tb_str = traceback.format_exc()
            logger.error(f"Failed to call RequestForInformationAgent (user clarification): {e}\n{tb_str}")
            log_path = os.path.join(os.path.dirname(__file__), 'log.txt')
            with open(log_path, 'a', encoding='utf-8') as logf:
                logf.write(f"[RequestForInformationAgent USER ERROR] {datetime.utcnow().isoformat()}\n{tb_str}\n")
            info_user_result = {
                "agent": "RequestForInformationAgent",
                "status": "error",
                "error": f"Failed to call RequestForInformationAgent (user clarification): {e}",
                "context": context
            }
            msg = create_message(
                sender="InvestigationAgent",
                receiver="RequestForInformationAgent",
                action="request_user_clarification",
                context=context,
                status="error",
                error={"message": str(e), "traceback": tb_str}
            )
            log_agent_message(msg, comment="Error calling RequestForInformationAgent (user clarification)")

        # --- Agent2Agent: Step 2: If user claim valid, ask RequestForInformationAgent for manager validation ---
        info_manager_result = None
        # Always proceed to manager validation, regardless of user clarification result
        try:
            # Build manager validation context
            manager_context = {
                **context,
                "clarification_type": "manager",
                "user_clarification_result": info_user_result.get("response", "") if info_user_result else ""
            }
            info_agent = RequestForInformationAgent()
            msg = create_message(
                sender="InvestigationAgent",
                receiver="RequestForInformationAgent",
                action="request_manager_validation",
                context=manager_context,
                status="pending"
            )
            log_agent_message(msg, comment="InvestigationAgent delegating to RequestForInformationAgent for manager approval flow")
            info_manager_result = await info_agent.handle_request(manager_context)
            # Log reasoning for RequestForInformationAgent (manager) step
            import json as _json
            info_manager_reasoning = info_manager_result.get("response") or info_manager_result.get("error") or info_manager_result.get("status")
            info_manager_reasoning_serialized = _json.dumps(info_manager_reasoning, ensure_ascii=False)
            msg2 = create_message(
                sender="RequestForInformationAgent",
                receiver="InvestigationAgent",
                action="response_manager_validation",
                context={**info_manager_result, "reasoning": info_manager_reasoning_serialized},
                status=info_manager_result.get("status", "unknown")
            )
            log_agent_message(msg2, comment="RequestForInformationAgent response to InvestigationAgent (manager approval)")
            msg3 = create_message(
                sender="InvestigationAgent",
                receiver="InvestigationAgent",
                action="received_informationagent_manager_response",
                context={**info_manager_result, "reasoning": info_manager_reasoning_serialized},
                status=info_manager_result.get("status", "unknown")
            )
            log_agent_message(msg3, comment="InvestigationAgent received response from RequestForInformationAgent (manager approval)")
            logger.info(f"InvestigationAgent received response from RequestForInformationAgent (manager approval): {info_manager_result}")
        except Exception as e:
            tb_str = traceback.format_exc()
            logger.error(f"Failed to call RequestForInformationAgent (manager approval): {e}\n{tb_str}")
            log_path = os.path.join(os.path.dirname(__file__), 'log.txt')
            with open(log_path, 'a', encoding='utf-8') as logf:
                logf.write(f"[RequestForInformationAgent MANAGER ERROR] {datetime.utcnow().isoformat()}\n{tb_str}\n")
            info_manager_result = {
                "agent": "RequestForInformationAgent",
                "status": "error",
                "error": f"Failed to call RequestForInformationAgent (manager approval): {e}",
                "context": manager_context
            }
            msg = create_message(
                sender="InvestigationAgent",
                receiver="RequestForInformationAgent",
                action="request_manager_validation",
                context=manager_context,
                status="error",
                error={"message": str(e), "traceback": tb_str}
            )
            log_agent_message(msg, comment="Error calling RequestForInformationAgent (manager approval)")

        # --- Agent2Agent: Final Step: Call AdvisoryAgent for report and mock email ---
        advisory_result = None
        try:
            from src.AdvisoryAgent import AdvisoryAgent
            advisory_agent = AdvisoryAgent()
            # Build advisory context: include all previous results and a flag to mock email
            advisory_context = {
                "mutation_id": context.get("mutation_id", "unknown"),
                "investigation": investigation_result,
                "rights_check": rights_result,
                "information_user_request": info_user_result,
                "information_manager_request": info_manager_result,
                "send_email_to_controller": True
            }
            msg = create_message(
                sender="InvestigationAgent",
                receiver="AdvisoryAgent",
                action="handle_request",
                context=advisory_context,
                status="pending"
            )
            log_agent_message(msg, comment="InvestigationAgent delegating to AdvisoryAgent for final report and email")
            advisory_result = await advisory_agent.handle_request(advisory_context)
            # Log reasoning for AdvisoryAgent step
            import json as _json
            advisory_reasoning = advisory_result.get("response") or advisory_result.get("error") or advisory_result.get("status")
            advisory_reasoning_serialized = _json.dumps(advisory_reasoning, ensure_ascii=False)
            msg2 = create_message(
                sender="AdvisoryAgent",
                receiver="InvestigationAgent",
                action="response",
                context={**advisory_result, "reasoning": advisory_reasoning_serialized},
                status=advisory_result.get("status", "unknown")
            )
            log_agent_message(msg2, comment="AdvisoryAgent response to InvestigationAgent (final report and email)")
            msg3 = create_message(
                sender="InvestigationAgent",
                receiver="InvestigationAgent",
                action="received_advisoryagent_response",
                context={**advisory_result, "reasoning": advisory_reasoning_serialized},
                status=advisory_result.get("status", "unknown")
            )
            log_agent_message(msg3, comment="InvestigationAgent received response from AdvisoryAgent (final report and email)")
            logger.info(f"InvestigationAgent received response from AdvisoryAgent: {advisory_result}")
        except Exception as e:
            tb_str = traceback.format_exc()
            logger.error(f"Failed to call AdvisoryAgent: {e}\n{tb_str}")
            log_path = os.path.join(os.path.dirname(__file__), 'log.txt')
            with open(log_path, 'a', encoding='utf-8') as logf:
                logf.write(f"[AdvisoryAgent ERROR] {datetime.utcnow().isoformat()}\n{tb_str}\n")
            advisory_result = {
                "agent": "AdvisoryAgent",
                "status": "error",
                "error": f"Failed to call AdvisoryAgent: {e}",
                "context": advisory_context if 'advisory_context' in locals() else {}
            }
            msg = create_message(
                sender="InvestigationAgent",
                receiver="AdvisoryAgent",
                action="handle_request",
                context=advisory_context if 'advisory_context' in locals() else {},
                status="error",
                error={"message": str(e), "traceback": tb_str}
            )
            log_agent_message(msg, comment="Error calling AdvisoryAgent for final report and email")

        # --- Return combined result ---
        return {
            "investigation": investigation_result,
            "rights_check": rights_result,
            "information_user_request": info_user_result,
            "information_manager_request": info_manager_result,
            "advisory_report": advisory_result
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