import os
import requests
from dotenv import load_dotenv
from InvestigationAgent import InvestigationAgent
from RightsCheckAgent import RightsCheckAgent
from RequestForInformationAgent import RequestForInformationAgent
from AdvisoryAgent import AdvisoryAgent
import logging

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

    def route(self, agent_name, context):
        """
        Route context to the specified agent and return the result dict.
        """
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Unknown agent: {agent_name}")
        return agent.handle_request(context)

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
