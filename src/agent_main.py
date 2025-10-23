
import os
import requests
from dotenv import load_dotenv
from src.InvestigationAgent import InvestigationAgent
from src.RightsCheckAgent import RightsCheckAgent
from src.RequestForInformationAgent import RequestForInformationAgent
from src.AdvisoryAgent import AdvisoryAgent
import logging
from src.agent_protocol import create_message, log_agent_message

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

MCV_SERVER_URL = os.getenv("MCV_SERVER_URL", "http://localhost:8000")

# --- MCV server tool call helpers ---
def mcv_authorization_check(user_id, system, access_level):
    url = f"{MCV_SERVER_URL}/api/authorization/check"
    payload = {"user_id": user_id, "system": system, "access_level": access_level}
    return requests.post(url, json=payload).json()

def mcv_data_lookup(file, query):
    url = f"{MCV_SERVER_URL}/api/data/lookup"
    payload = {"file": file, "query": query}
    return requests.post(url, json=payload).json()

def mcv_notify_send(recipient_id, subject, body, context=None):
    url = f"{MCV_SERVER_URL}/api/notify/send"
    payload = {"recipient_id": recipient_id, "subject": subject, "body": body, "context": context or {}}
    return requests.post(url, json=payload).json()

def mcv_report_generate(mutation_id, context):
    url = f"{MCV_SERVER_URL}/api/report/generate"
    payload = {"mutation_id": mutation_id, "context": context}
    return requests.post(url, json=payload).json()


# --- Agent orchestrator for Azure model-based agents ---
class AgentOrchestrator:
    def __init__(self):
        self.agents = {
            "InvestigationAgent": InvestigationAgent(),
            "RightsCheckAgent": RightsCheckAgent(),
            "RequestForInformationAgent": RequestForInformationAgent(),
            "AdvisoryAgent": AdvisoryAgent(),
        }

    def route(self, agent_name, context, max_retries=3, sender="Orchestrator", action="handle_request"):
        """
        Route context to the specified agent using Agent2Agent protocol.
        Retries on error, escalates after max_retries.
        Logs all messages and responses.
        """
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Unknown agent: {agent_name}")
        attempt = 0
        last_result = None
        correlation_id = None
        while attempt < max_retries:
            # Create and log Agent2Agent protocol message
            msg = create_message(
                sender=sender,
                receiver=agent_name,
                action=action,
                context=context,
                status="pending" if attempt == 0 else "retry",
                correlation_id=correlation_id
            )
            log_agent_message(msg)
            correlation_id = msg.correlation_id
            # Call agent
            result = agent.handle_request(context)
            # Log response as Agent2Agent message
            resp_msg = create_message(
                sender=agent_name,
                receiver=sender,
                action=f"{action}_result",
                context=result.get("context", context),
                status=result.get("status", "unknown"),
                correlation_id=correlation_id,
                error={"error": result.get("error")} if result.get("status") == "error" else None
            )
            log_agent_message(resp_msg)
            last_result = result
            if result.get("status") != "error":
                return result
            logging.error(f"{agent_name} error on attempt {attempt+1}: {result.get('error')}")
            attempt += 1
        # Escalate after retries exhausted
        logging.error(f"{agent_name} failed after {max_retries} attempts. Escalating to manual intervention.")
        escalation = {
            "agent": agent_name,
            "status": "escalated",
            "error": last_result.get("error") if last_result else "Unknown error",
            "context": context,
            "escalation": "Manual intervention required after repeated failures.",
            "correlation_id": correlation_id
        }
        # Log escalation as Agent2Agent message
        esc_msg = create_message(
            sender=agent_name,
            receiver=sender,
            action=f"{action}_escalation",
            context=context,
            status="escalated",
            correlation_id=correlation_id,
            error={"error": escalation["error"]}
        )
        log_agent_message(esc_msg)
        return escalation

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    orchestrator = AgentOrchestrator()
    # Full end-to-end workflow
    initial_context = {
        "mutation_id": "1001",
        "user_id": "u001",
        "system": "Payroll",
        "access_level": "Admin",
        "old_status": "Pending",
        "new_status": "Investigation Started"
    }
    # Step 1: InvestigationAgent
    result1 = orchestrator.route("InvestigationAgent", initial_context)
    logging.info(f"InvestigationAgent result: {result1}")
    # Step 2: RightsCheckAgent
    result2 = orchestrator.route("RightsCheckAgent", result1.get("context", {}))
    logging.info(f"RightsCheckAgent result: {result2}")
    # Step 3: RequestForInformationAgent
    result3 = orchestrator.route("RequestForInformationAgent", result2.get("context", {}))
    logging.info(f"RequestForInformationAgent result: {result3}")
    # Step 4: AdvisoryAgent
    result4 = orchestrator.route("AdvisoryAgent", result3.get("context", {}))
    logging.info(f"AdvisoryAgent result: {result4}")
    # Step 5: (Optional) Loop back or finalize as needed
    print("Workflow complete. Advisory report:", result4.get("response"))
